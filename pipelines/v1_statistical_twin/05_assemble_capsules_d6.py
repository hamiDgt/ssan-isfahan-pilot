import pandas as pd
import h3
from neo4j import GraphDatabase

iss = pd.read_parquet('/home/hmid/ssan-data/iss_cells_d6.parquet')
gss = pd.read_parquet('/home/hmid/ssan-data/d6_gss_context.parquet')

counts = iss.groupby('h3_index').agg(iss_count=('iss_id','count'), support=('expansion_weight','sum')).reset_index()
counts['final_id'] = [h if c >= 30 else h3.cell_to_parent(h, 8) for h, c in zip(counts['h3_index'], counts['iss_count'])]
merge_map = dict(zip(counts['h3_index'], counts['final_id']))

iss['final_id'] = iss['h3_index'].map(merge_map)
caps = iss.groupby('final_id').agg(iss_count=('iss_id','count'), support=('expansion_weight','sum'), mean_age=('age','mean'), mean_wealth=('wealth_proxy','mean')).reset_index()

cg = counts.merge(gss[['h3_index','gss_context']], on='h3_index', how='left')
cg['gss_context'] = cg['gss_context'].fillna(0.0)
cg['wg'] = cg['gss_context'] * cg['support']
num = cg.groupby('final_id')['wg'].sum()
den = cg.groupby('final_id')['support'].sum()
caps = caps.merge((num/den).rename('gss').reset_index(), on='final_id')

caps['resolution'] = [h3.get_resolution(f) for f in caps['final_id']]
caps['center_lat'] = [h3.cell_to_latlng(f)[0] for f in caps['final_id']]
caps['center_lon'] = [h3.cell_to_latlng(f)[1] for f in caps['final_id']]
caps['reliable'] = caps['support'] >= 30

final_ids = set(caps['final_id'])
edges = set()
for f in caps['final_id']:
    for n in h3.grid_ring(f, 1):
        if n in final_ids: edges.add((f, n))
        elif n in merge_map: edges.add((f, merge_map[n]))
    if h3.get_resolution(f) == 8:
        for child in h3.cell_to_children(f, 9):
            if child in final_ids: edges.add((f, child))

    pd.DataFrame([[s, 'neighborOf', d] for s, d in edges]).to_csv('/home/hmid/ssan-data/pykeen_edges.tsv', sep='	', index=False, header=False)
caps.to_parquet('/home/hmid/ssan-data/capsules_d6.parquet', index=False)

driver = GraphDatabase.driver("bolt://localhost:7687")
with driver.session() as session:
    session.run("MATCH (c:Capsule) DETACH DELETE c")
    rows = [{'h3': r.final_id, 'lat': float(r.center_lat), 'lon': float(r.center_lon), 'iss': float(r.support), 'gss': float(r.gss), 'res': int(r.resolution), 'cnt': int(r.iss_count), 'age': float(r.mean_age), 'wealth': float(r.mean_wealth), 'rel': bool(r.reliable)} for r in caps.itertuples()]
    session.run("UNWIND $rows AS r CREATE (c:Capsule {h3_index: r.h3, center_lat: r.lat, center_lon: r.lon, iss_weight: r.iss, gss_context: r.gss, resolution: r.res, iss_count: r.cnt, mean_age: r.age, mean_wealth: r.wealth, reliable: r.rel})", rows=rows)
    erows = [{'s': s, 'd': d} for s, d in edges]
    session.run("UNWIND $rows AS r MATCH (a:Capsule {h3_index: r.s}), (b:Capsule {h3_index: r.d}) CREATE (a)-[:NEIGHBOR_OF]->(b)", rows=erows)
driver.close()
print(f"D6 capsules: {len(caps)}, edges: {len(edges)}")

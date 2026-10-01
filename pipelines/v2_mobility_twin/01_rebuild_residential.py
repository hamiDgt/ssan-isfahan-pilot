import json, h3, numpy as np, pandas as pd
from neo4j import GraphDatabase

np.random.seed(42)
RES, TARGET_ISS, TARGET_POP = 10, 20000, 112129
EXCLUDE = {'industrial','warehouse','garage','garages','shed','factory','hangar','barn','commercial','retail','office','kiosk','roof','bridge','construction','military'}

with open('/home/hmid/ssan-data/osm/d6_buildings.json') as f:
    bldg = json.load(f)

rows = []
for e in bldg['elements']:
    if 'center' not in e: continue
    tag = e.get('tags', {}).get('building', 'yes')
    if tag in EXCLUDE: continue
    rows.append({'lat': e['center']['lat'], 'lon': e['center']['lon'], 'tag': tag})
df_b = pd.DataFrame(rows)
print(f"Kept {len(df_b)} residential buildings of {len(bldg['elements'])}")

df_b['h3_index'] = [h3.latlng_to_cell(a, b, RES) for a, b in zip(df_b.lat, df_b.lon)]
bcount = df_b.groupby('h3_index').size().reset_index(name='building_count')
bcount['population'] = bcount['building_count'] / bcount['building_count'].sum() * TARGET_POP

print("Top 5 population hexagons after filter:")
for _, r in bcount.nlargest(5, 'building_count').iterrows():
    tags = df_b[df_b.h3_index == r.h3_index]['tag'].value_counts().head(2).to_dict()
    print(f"  {r.h3_index} pop={int(r.population)} tags={tags}")

cal9 = pd.read_parquet('/home/hmid/ssan-data/d6_silver_calibrated.parquet')
rad_map = {}
for h, rad in zip(cal9.h3_index, cal9.radiance):
    for child in h3.cell_to_children(h, RES):
        rad_map[child] = rad
bcount['radiance'] = bcount['h3_index'].map(rad_map).fillna(0.0)

bcount['target_cells'] = (bcount['population'] / TARGET_POP * TARGET_ISS).round(0).astype(int).clip(1)
iss_records = []
for _, row in bcount.iterrows():
    n = int(row.target_cells)
    ages = np.random.normal(30, 15, n).clip(0, 100).astype(int)
    wealth = np.random.normal(row.radiance, 5, n).clip(0, 63)
    w = row.population / n
    for i in range(n):
        iss_records.append({'iss_id': f"ISS_{row.h3_index}_{i}", 'h3_index': row.h3_index, 'age': int(ages[i]), 'wealth_proxy': float(wealth[i]), 'expansion_weight': float(w)})
iss = pd.DataFrame(iss_records)

caps = iss.groupby('h3_index').agg(iss_count=('iss_id','count'), support=('expansion_weight','sum'), mean_age=('age','mean'), mean_wealth=('wealth_proxy','mean')).reset_index().rename(columns={'h3_index':'final_id'})

gss9 = pd.read_parquet('/home/hmid/ssan-data/d6_gss_context.parquet')
gmap = {}
for h, g in zip(gss9.h3_index, gss9.gss_context):
    for child in h3.cell_to_children(h, RES):
        gmap[child] = g
caps['gss'] = caps['final_id'].map(gmap).fillna(0.0)
caps['resolution'] = 10
caps['center_lat'] = [h3.cell_to_latlng(f)[0] for f in caps.final_id]
caps['center_lon'] = [h3.cell_to_latlng(f)[1] for f in caps.final_id]
caps['reliable'] = caps.support >= 30

fset, edges = set(caps.final_id), set()
for f in caps.final_id:
    for n in h3.grid_ring(f, 1):
        if n in fset: edges.add((f, n))

caps.to_parquet('/home/hmid/ssan-data/capsules_d6.parquet', index=False)
iss.to_parquet('/home/hmid/ssan-data/iss_cells_d6.parquet', index=False)
agents = iss.rename(columns={'iss_id':'agent_id','h3_index':'location','wealth_proxy':'wealth','expansion_weight':'weight'})[['agent_id','location','age','wealth','weight']]
agents.to_json('/home/hmid/ssan-data/mesa_agents.json', orient='records')

driver = GraphDatabase.driver("bolt://localhost:7687")
with driver.session() as session:
    session.run("MATCH (c:Capsule) DETACH DELETE c")
    session.run("UNWIND $rows AS r CREATE (c:Capsule {h3_index: r.h3, center_lat: r.lat, center_lon: r.lon, iss_weight: r.iss, gss_context: r.gss, resolution: r.res, iss_count: r.cnt, mean_age: r.age, mean_wealth: r.wealth, reliable: r.rel})",
        rows=[{'h3': r.final_id, 'lat': float(r.center_lat), 'lon': float(r.center_lon), 'iss': float(r.support), 'gss': float(r.gss), 'res': int(r.resolution), 'cnt': int(r.iss_count), 'age': float(r.mean_age), 'wealth': float(r.mean_wealth), 'rel': bool(r.reliable)} for r in caps.itertuples()])
    session.run("UNWIND $rows AS r MATCH (a:Capsule {h3_index: r.s}), (b:Capsule {h3_index: r.d}) CREATE (a)-[:NEIGHBOR_OF]->(b)", rows=[{'s': s, 'd': d} for s, d in edges])
driver.close()
print(f"Final: {len(caps)} capsules, {len(edges)} edges, {len(iss)} ISS agents.")

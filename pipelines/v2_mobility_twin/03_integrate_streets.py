import osmnx as ox
import networkx as nx
import pandas as pd
import json
import h3
from neo4j import GraphDatabase

caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
nodes_df = pd.read_parquet('/home/hmid/ssan-data/street_nodes.parquet')
edges_df = pd.read_parquet('/home/hmid/ssan-data/street_edges.parquet')

G = nx.MultiDiGraph()
G.graph['crs'] = 'epsg:4326'
for _, row in nodes_df.iterrows():
    G.add_node(row['node'], y=row['lat'], x=row['lon'])
for _, row in edges_df.iterrows():
    G.add_edge(row['u'], row['v'], length=row['length'])

print("Mapping capsules to street nodes...")
caps_nodes = ox.distance.nearest_nodes(G, caps['center_lon'].values, caps['center_lat'].values)
caps['street_node'] = caps_nodes

cap_to_node = dict(zip(caps['final_id'], caps['street_node']))
cap_set = set(caps['final_id'])

print("Calculating edge weights...")
edges = []
for f in caps['final_id']:
    u_node = cap_to_node[f]
    for n in h3.grid_ring(f, 1):
        if n in cap_set:
            v_node = cap_to_node[n]
            try:
                dist = nx.shortest_path_length(G, u_node, v_node, weight='length')
            except nx.NetworkXNoPath:
                dist = 500.0
            edges.append({'src': f, 'dst': n, 'weight': max(1.0, float(dist))})

edges_df_h3 = pd.DataFrame(edges)
edges_df_h3.to_csv('/home/hmid/ssan-data/weighted_edges.csv', index=False)

print("Extracting transit attractors...")
with open('/home/hmid/ssan-data/osm/d6_transit.json') as f:
    transit_data = json.load(f)

t_lons, t_lats = [], []
for e in transit_data['elements']:
    if 'lat' in e and 'lon' in e:
        t_lons.append(e['lon'])
        t_lats.append(e['lat'])

if t_lons:
    t_nodes = ox.distance.nearest_nodes(G, t_lons, t_lats)
    attr_df = pd.DataFrame({'lat': t_lats, 'lon': t_lons, 'street_node': t_nodes})
    node_to_cap = {v: k for k, v in cap_to_node.items()}
    attr_df['capsule'] = attr_df['street_node'].map(node_to_cap)
    attr_df = attr_df.dropna(subset=['capsule'])
else:
    attr_df = pd.DataFrame(columns=['lat', 'lon', 'street_node', 'capsule'])

attr_df.to_csv('/home/hmid/ssan-data/transit_attractors.csv', index=False)

print("Updating Memgraph...")
driver = GraphDatabase.driver("bolt://localhost:7687")
with driver.session() as session:
    session.run("MATCH ()-[r:NEIGHBOR_OF]->() DELETE r")
    session.run("""
        UNWIND $rows AS r
        MATCH (a:Capsule {h3_index: r.src}), (b:Capsule {h3_index: r.dst})
        CREATE (a)-[:NEIGHBOR_OF {weight: r.weight}]->(b)
    """, rows=edges_df_h3.to_dict('records'))
driver.close()

print(f"Updated Memgraph with {len(edges_df_h3)} weighted edges.")
print(f"Extracted {len(attr_df)} transit attractors.")

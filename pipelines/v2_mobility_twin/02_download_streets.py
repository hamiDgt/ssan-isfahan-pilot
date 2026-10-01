import osmnx as ox
import pandas as pd
from shapely.geometry import MultiPoint
import json

with open('/home/hmid/ssan-data/osm/district6_boundary.json') as f:
    data = json.load(f)

points = []
for e in data['elements']:
    if 'lat' in e: points.append((e['lon'], e['lat']))
    if 'geometry' in e:
        for pt in e['geometry']: points.append((pt['lon'], pt['lat']))
    if 'members' in e:
        for m in e['members']:
            if 'lat' in m: points.append((m['lon'], m['lat']))
            if 'geometry' in m:
                for pt in m['geometry']: points.append((pt['lon'], pt['lat']))

poly = MultiPoint(points).convex_hull
print(f"Polygon valid: {poly.is_valid}, area: {poly.area:.4f}")

G = ox.graph_from_polygon(poly, network_type='walk')
print(f"Street network: {len(G.nodes)} nodes, {len(G.edges)} edges")

edges = []
for u, v, k, d in G.edges(keys=True, data=True):
    hw = d.get('highway', 'unknown')
    if isinstance(hw, list): hw = hw[0]
    edges.append({'u': u, 'v': v, 'length': d.get('length', 0), 'highway': hw, 'bridge': 1 if d.get('bridge') else 0})
pd.DataFrame(edges).to_parquet('/home/hmid/ssan-data/street_edges.parquet', index=False)

nodes = []
for n, d in G.nodes(data=True):
    nodes.append({'node': n, 'lat': d['y'], 'lon': d['x']})
pd.DataFrame(nodes).to_parquet('/home/hmid/ssan-data/street_nodes.parquet', index=False)
print("Saved street network.")

import json, random, collections, math
import networkx as nx, numpy as np, pandas as pd, h3

np.random.seed(42)
random.seed(42)

EXCLUDE = {'industrial','warehouse','garage','garages','shed','factory','hangar','barn','commercial','retail','office','kiosk','roof','bridge','construction','military'}

iss = pd.read_parquet('/home/hmid/ssan-data/iss_cells_d6.parquet')
caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
silver = pd.read_parquet('/home/hmid/ssan-data/silver_full.parquet')
edges_df = pd.read_csv('/home/hmid/ssan-data/weighted_edges.csv')
with open('/home/hmid/ssan-data/osm/d6_buildings.json') as f:
    bldg = json.load(f)

brows = []
for e in bldg['elements']:
    if 'center' not in e: continue
    tag = e.get('tags', {}).get('building', 'yes')
    if tag in EXCLUDE: continue
    brows.append({'bid': e['id'], 'lat': e['center']['lat'], 'lon': e['center']['lon']})
bdf = pd.DataFrame(brows)
bdf['h3_index'] = [h3.latlng_to_cell(a, b, 10) for a, b in zip(bdf.lat, bdf.lon)]

capset = set(caps.final_id)
b_per_cap = bdf[bdf.h3_index.isin(capset)].groupby('h3_index')['bid'].apply(list).to_dict()

N = len(iss)
h3list = list(iss.h3_index)
age = list(iss.age)
wealth = list(iss.wealth_proxy)

person_building = [random.choice(b_per_cap[h]) if h in b_per_cap else None for h in h3list]

# Gravity attractors for activity ties
bbox = (32.5416814, 51.6627253, 32.6446693, 51.7650088)
s = silver[(silver.lat >= bbox[0]) & (silver.lon >= bbox[1]) & (silver.lat <= bbox[2]) & (silver.lon <= bbox[3])].copy()
w_map = {'shop': 3.0, 'amenity': 2.0, 'tourism': 2.0, 'leisure': 1.0}
s['att'] = s.category.map(w_map).fillna(0.5)

def point_to_cap(lat, lon):
    h = h3.latlng_to_cell(lat, lon, 10)
    if h in capset: return h
    h = h3.cell_to_parent(h, 9)
    if h in capset: return h
    h = h3.cell_to_parent(h, 8)
    if h in capset: return h
    return None

s['cap'] = [point_to_cap(a, b) for a, b in zip(s.lat, s.lon)]
agg = s.dropna(subset=['cap']).groupby('cap')['att'].sum().to_dict()
cc = caps.set_index('final_id')[['center_lat', 'center_lon']]
latd, lond = cc['center_lat'].to_dict(), cc['center_lon'].to_dict()
a_caps = list(agg.keys())
a_vals = np.clip(np.array([agg[c] for c in a_caps]), None, np.percentile([agg[c] for c in a_caps], 90))
a_lats = np.array([latd[c] for c in a_caps])
a_lons = np.array([lond[c] for c in a_caps])

person_attractor = []
for h in h3list:
    dy = (a_lats - latd[h]) * 111.0
    dx = (a_lons - lond[h]) * 111.0 * np.cos(np.radians(latd[h]))
    d = np.sqrt(dx*dx + dy*dy)
    w = a_vals / (1.0 + d) ** 1.5
    person_attractor.append(a_caps[int(np.random.choice(len(a_caps), p=w/w.sum()))])

edges = set()
type_counts = [0, 0, 0, 0]

# Type 0: residence ties (same real building)
by_bld = collections.defaultdict(list)
for i, b in enumerate(person_building):
    if b: by_bld[b].append(i)
for members in by_bld.values():
    if len(members) < 2: continue
    for p in members:
        others = [m for m in members if m != p]
        for q in random.sample(others, min(2, len(others))):
            edges.add((min(p, q), max(p, q), 0)); type_counts[0] += 1

# Type 1: neighbor ties (same capsule, different building)
by_cap = collections.defaultdict(list)
for i, h in enumerate(h3list):
    by_cap[h].append(i)
for i, h in enumerate(h3list):
    members = by_cap[h]
    if len(members) < 2: continue
    q = random.choice(members)
    if q != i:
        edges.add((min(i, q), max(i, q), 1)); type_counts[1] += 1

# Type 2: activity ties (same daytime attractor)
by_attr = collections.defaultdict(list)
for i, a in enumerate(person_attractor):
    by_attr[a].append(i)
for i, a in enumerate(person_attractor):
    members = by_attr[a]
    if len(members) < 2: continue
    q = random.choice(members)
    if q != i:
        edges.add((min(i, q), max(i, q), 2)); type_counts[2] += 1

# Type 3: homophily ties (adjacent capsule, similar age and wealth)
adj_caps = collections.defaultdict(set)
for _, r in edges_df.iterrows():
    adj_caps[r['src']].add(r['dst'])
    adj_caps[r['src']].add(r['dst'])
    adj_caps[r['dst']].add(r['src'])
for i, h in enumerate(h3list):
    nbs = [n for n in adj_caps.get(h, []) if n in by_cap]
    for _ in range(3):
        if not nbs: break
        n = random.choice(nbs)
        cands = [m for m in by_cap[n] if abs(wealth[m] - wealth[i]) <= 5 and abs(age[m] - age[i]) <= 10]
        if cands:
            q = random.choice(cands)
            edges.add((min(i, q), max(i, q), 3)); type_counts[3] += 1
            break

edges = sorted(edges)
print(f"Ties: residence={type_counts[0]} neighbor={type_counts[1]} activity={type_counts[2]} homophily={type_counts[3]} total={len(edges)}")

G = nx.Graph()
G.add_nodes_from(range(N))
G.add_edges_from([(a, b) for a, b, t in edges])
comms = nx.community.label_propagation_communities(G)
comm_id = {}
for cid, comp in enumerate(comms):
    for n in comp:
        comm_id[n] = cid
print(f"Communities: {len(comms)}")

cap_list = sorted(capset)
capidx = {c: i for i, c in enumerate(cap_list)}
persons = [[int(age[i]), round(float(wealth[i]), 1), comm_id[i], capidx[h3list[i]]] for i in range(N)]

with open('/home/hmid/ssan-data/person_network.json', 'w') as f:
    json.dump({'persons': persons, 'edges': [list(e) for e in edges]}, f)
print("Saved person_network.json")

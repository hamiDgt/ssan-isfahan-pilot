import json, random, collections
import networkx as nx, numpy as np, pandas as pd, h3

np.random.seed(7)
random.seed(7)

edges_df = pd.read_csv('/home/hmid/ssan-data/weighted_edges.csv')
caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
silver = pd.read_parquet('/home/hmid/ssan-data/silver_full.parquet')
transit = pd.read_csv('/home/hmid/ssan-data/transit_attractors.csv')
agents_raw = json.load(open('/home/hmid/ssan-data/mesa_agents.json'))

G = nx.MultiDiGraph()
for _, row in edges_df.iterrows():
    G.add_edge(row['src'], row['dst'], weight=row['weight'])
capset = set(G.nodes)

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
for c in transit['capsule']:
    if c in capset:
        agg[c] = agg.get(c, 0.0) + 2.0
print(f"Attractor capsules: {len(agg)}")

cap_coords = caps.set_index('final_id')[['center_lat', 'center_lon']]
a_caps = list(agg.keys())
a_lats = np.array([cap_coords.loc[c, 'center_lat'] for c in a_caps])
a_lons = np.array([cap_coords.loc[c, 'center_lon'] for c in a_caps])
a_vals = np.array([agg[c] for c in a_caps])

samples = {}
for c in capset:
    lat0, lon0 = cap_coords.loc[c, 'center_lat'], cap_coords.loc[c, 'center_lon']
    dy = (a_lats - lat0) * 111.0
    dx = (a_lons - lon0) * 111.0 * np.cos(np.radians(lat0))
    d = np.sqrt(dx*dx + dy*dy)
    w = a_vals / (1.0 + d) ** 2
    tot = w.sum()
    if tot <= 0:
        samples[c] = list(np.random.choice(a_caps, 20))
    else:
        samples[c] = list(np.random.choice(a_caps, 20, p=w/tot))

agents = []
for a in agents_raw:
    loc = a['location'] if a['location'] in capset else random.choice(list(capset))
    agents.append([loc, []])

edge_counts = collections.Counter()
print("Running 50 gravity steps...")
for step in range(50):
    for ag in agents:
        loc, path = ag[0], ag[1]
        if not path:
            target = random.choice(samples[loc])
            if target != loc:
                try:
                    path = nx.shortest_path(G, loc, target, weight='weight')[1:]
                except Exception:
                    path = []
            ag[1] = path
        if path:
            nxt = path.pop(0)
        else:
            succ = list(G.successors(loc))
            if not succ:
                continue
            ws = [1.0 / G[loc][t][0]['weight'] for t in succ]
            nxt = random.choices(succ, weights=ws, k=1)[0]
        edge_counts[(loc, nxt)] += 1
        ag[0] = nxt

print("=== GRAVITY PLANNER TEST: Top 10 corridors ===")
for (a, b), c in edge_counts.most_common(10):
    la, lo = cap_coords.loc[a, 'center_lat'], cap_coords.loc[a, 'center_lon']
    lb, ob = cap_coords.loc[b, 'center_lat'], cap_coords.loc[b, 'center_lon']
    print(f"{la:.5f}, {lo:.5f} -> {lb:.5f}, {ob:.5f} | {c}")

shock = min(capset, key=lambda c: (cap_coords.loc[c,'center_lat']-32.5525)**2 + (cap_coords.loc[c,'center_lon']-51.6900)**2)
print(f"Shock at City Center proxy: {shock}")

passages = collections.Counter()
evac = []
for a in agents_raw:
    loc = a['location']
    if loc not in capset: continue
    try:
        if h3.grid_distance(loc, shock) <= 2:
            evac.append([loc])
    except Exception:
        pass
print(f"Evacuating {len(evac)} agents for 30 steps...")
for step in range(30):
    for ev in evac:
        loc = ev[0]
        best, bd = None, -1
        for t in G.successors(loc):
            try:
                d = h3.grid_distance(t, shock)
            except Exception:
                d = 0
            if d > bd:
                bd, best = d, t
        if best is not None:
            passages[best] += 1
            ev[0] = best

print("=== RESPONDER TEST V2: Top 5 bottlenecks ===")
for n, c in passages.most_common(5):
    print(f"{cap_coords.loc[n,'center_lat']:.5f}, {cap_coords.loc[n,'center_lon']:.5f} | passages {c}")

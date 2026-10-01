import os
import json, random, collections, math
import networkx as nx, numpy as np, pandas as pd, h3, osmnx as ox

np.random.seed(7)
random.seed(7)

edges_df = pd.read_csv('/home/hmid/ssan-data/weighted_edges.csv')
caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
silver = pd.read_parquet('/home/hmid/ssan-data/silver_full.parquet')
cal9 = pd.read_parquet('/home/hmid/ssan-data/d6_silver_calibrated.parquet')
transit = pd.read_csv('/home/hmid/ssan-data/transit_attractors.csv')
agents_raw = json.load(open('/home/hmid/ssan-data/mesa_agents.json'))
pnet = json.load(open('/home/hmid/ssan-data/person_network.json'))
sn = pd.read_parquet('/home/hmid/ssan-data/street_nodes.parquet')
se = pd.read_parquet('/home/hmid/ssan-data/street_edges.parquet')

S = nx.MultiDiGraph()
S.graph['crs'] = 'epsg:4326'
for _, r in sn.iterrows(): S.add_node(r['node'], y=r['lat'], x=r['lon'])
for _, r in se.iterrows(): S.add_edge(r['u'], r['v'], length=r['length'])
spos = {n: (d['y'], d['x']) for n, d in S.nodes(data=True)}

G = nx.MultiDiGraph()
for _, r in edges_df.iterrows(): G.add_edge(r['src'], r['dst'], weight=r['weight'])
capset = set(G.nodes)
cc = caps.set_index('final_id')[['center_lat', 'center_lon', 'support']]
latd, lond, supd = cc['center_lat'].to_dict(), cc['center_lon'].to_dict(), cc['support'].to_dict()

print("Computing street polylines...")
PATHS = {}
for _, r in edges_df.iterrows():
    a, b = r['src'], r['dst']
    na = ox.distance.nearest_nodes(S, [lond[a]], [latd[a]])[0]
    nb = ox.distance.nearest_nodes(S, [lond[b]], [latd[b]])[0]
    try:
        seq = nx.shortest_path(S, na, nb, weight='length')
    except Exception:
        seq = [na, nb]
    pts = [spos[n] for n in seq]
    if len(pts) > 12:
        idx = np.linspace(0, len(pts)-1, 12).astype(int)
        pts = [pts[i] for i in idx]
    PATHS[f"{a}|{b}"] = [round(v, 5) for p in pts for v in p]

# Nightlight polygons
vals = [v for v in cal9.radiance if v > 0]
vmax = max(vals)
def ncolor(v):
    t = math.log1p(v) / math.log1p(vmax)
    return f"#{int(26+229*t):02x}{int(26+187*t):02x}{int(94-15*t):02x}", round(0.15 + 0.4 * t, 2)
NIGHT = []
for h, v in zip(cal9.h3_index, cal9.radiance):
    if v <= 0: continue
    col, op = ncolor(v)
    ring = h3.cell_to_boundary(h)
    NIGHT.append([round(c, 5) for pt in ring for c in pt] + [col, op])

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
    if c in capset: agg[c] = agg.get(c, 0.0) + 2.0

a_caps = list(agg.keys())
a_vals = np.clip(np.array([agg[c] for c in a_caps]), None, np.percentile([agg[c] for c in a_caps], 90))
a_lats = np.array([latd[c] for c in a_caps])
a_lons = np.array([lond[c] for c in a_caps])
samples = {}
for c in capset:
    dy = (a_lats - latd[c]) * 111.0
    dx = (a_lons - lond[c]) * 111.0 * np.cos(np.radians(latd[c]))
    d = np.sqrt(dx*dx + dy*dy)
    w = a_vals / (1.0 + d) ** 1.5
    samples[c] = list(np.random.choice(a_caps, 20, p=w/w.sum()))

agents = []
for a in agents_raw:
    loc = a['location'] if a['location'] in capset else random.choice(list(capset))
    agents.append([loc, []])

cap_list = sorted(capset)
capidx = {c: i for i, c in enumerate(cap_list)}
CAPS = [[round(latd[c], 5), round(lond[c], 5), round(float(supd[c]), 0), c] for c in cap_list]

JIT = []
for _ in agents:
    JIT += [round(random.uniform(-0.0006, 0.0006), 5), round(random.uniform(-0.0006, 0.0006), 5)]

frames = []
print(f"Running 50 gravity steps with {len(agents)} agents...")
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
            ag[0] = path.pop(0)
        else:
            succ = list(G.successors(loc))
            if succ:
                ws = [1.0 / G[loc][t][0]['weight'] for t in succ]
                ag[0] = random.choices(succ, weights=ws, k=1)[0]
    frames.append([capidx[ag[0]] for ag in agents])

edge_counts = collections.Counter()
for t in range(len(frames)-1):
    for k in range(len(agents)):
        if frames[t][k] != frames[t+1][k]:
            edge_counts[(cap_list[frames[t][k]], cap_list[frames[t+1][k]])] += 1
CORR = [[f"{a}|{b}", c] for (a, b), c in edge_counts.most_common(40)]
ATTR = [[round(latd[c], 5), round(lond[c], 5)] for c, _ in sorted(agg.items(), key=lambda x: -x[1])[:30] if c in latd]

template = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'twin_template_v3.html')).read()
html = (template.replace('__CAPS__', json.dumps(CAPS))
    .replace('__PATHS__', json.dumps(PATHS))
    .replace('__FRAMES__', json.dumps(frames))
    .replace('__JIT__', json.dumps(JIT))
    .replace('__CORR__', json.dumps(CORR))
    .replace('__ATTR__', json.dumps(ATTR))
    .replace('__NIGHT__', json.dumps(NIGHT))
    .replace('__PERSONS__', json.dumps(pnet['persons']))
    .replace('__EDGES__', json.dumps(pnet['edges']))
    .replace('__MAXSTEP__', str(len(frames)-1)))
with open('/home/hmid/ssan-data/isfahan_twin_v3.html', 'w') as f:
    f.write(html)
print(f"Saved living map v3 ({len(html)/1e6:.1f} MB)")

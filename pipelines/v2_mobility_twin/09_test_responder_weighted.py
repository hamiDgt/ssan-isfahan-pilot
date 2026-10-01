import pandas as pd
import networkx as nx
import h3

edges_df = pd.read_csv('/home/hmid/ssan-data/weighted_edges.csv')
caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet').set_index('final_id')
street_edges = pd.read_parquet('/home/hmid/ssan-data/street_edges.parquet')

G = nx.MultiDiGraph()
for _, row in edges_df.iterrows():
    G.add_edge(row['src'], row['dst'], weight=row['weight'])

shock = caps['support'].idxmax()
print(f"Shock at densest node: {shock} ({caps.loc[shock, 'center_lat']:.5f}, {caps.loc[shock, 'center_lon']:.5f})")

bottlenecks = {}
for node in G.nodes():
    try:
        dist = h3.grid_distance(node, shock)
    except Exception:
        dist = 99
    if dist <= 3:
        succ = list(G.successors(node))
        for s in succ:
            try:
                d = h3.grid_distance(s, shock)
                if d > dist:
                    bottlenecks[s] = bottlenecks.get(s, 0) + 1
            except Exception:
                pass

top5 = sorted(bottlenecks.items(), key=lambda x: -x[1])[:5]
print("=== WEIGHTED RESPONDER TEST: Top 5 Evacuation Bottlenecks ===")
for n, sc in top5:
    if n in caps.index:
        print(f"{caps.loc[n,'center_lat']:.5f}, {caps.loc[n,'center_lon']:.5f} | Jam Score: {sc}")

# Check if any bottlenecks are on bridges
bridges = street_edges[street_edges['bridge'] == 1]
print(f"\nTotal bridge edges in street network: {len(bridges)}")

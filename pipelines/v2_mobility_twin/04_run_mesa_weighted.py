import random
import networkx as nx
import pandas as pd
import numpy as np
import json

edges_df = pd.read_csv('/home/hmid/ssan-data/weighted_edges.csv')
attr_df = pd.read_csv('/home/hmid/ssan-data/transit_attractors.csv')
agents = json.load(open('/home/hmid/ssan-data/mesa_agents.json'))

G = nx.MultiDiGraph()
for _, row in edges_df.iterrows():
    G.add_edge(row['src'], row['dst'], weight=row['weight'])

# Ensure all agent starting locations are in the graph
all_caps = set(edges_df['src']).union(set(edges_df['dst']))
for a in agents:
    if a['location'] not in all_caps:
        a['location'] = random.choice(list(all_caps))

attractor_capsules = [c for c in attr_df['capsule'].tolist() if c in all_caps]

class Agent:
    def __init__(self, agent_id, location, wealth, weight):
        self.agent_id = agent_id
        self.location = location
        self.wealth = wealth
        self.weight = weight

agents = [Agent(a['agent_id'], a['location'], a['wealth'], a['weight']) for a in agents]
print(f"Initializing weighted Mesa model with {len(agents)} agents...")

results = []
print("Running 20 simulation steps with street weights and attractors...")
for step in range(20):
    random.shuffle(agents)
    for a in agents:
        a.wealth += np.random.normal(0, 0.5)
        
        if a.location not in G:
            continue
            
        # 10% chance to travel to a transit attractor
        if random.random() < 0.1 and len(attractor_capsules) > 0:
            target = random.choice(attractor_capsules)
            try:
                path = nx.shortest_path(G, a.location, target, weight='weight')
                if len(path) > 1:
                    a.location = path[1]
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                pass
        else:
            succ = list(G.successors(a.location))
            if succ:
                weights = [1.0 / G[a.location][s][0]['weight'] for s in succ]
                total = sum(weights)
                probs = [w / total for w in weights]
                a.location = random.choices(succ, weights=probs, k=1)[0]
                
    if step == 19:
        for a in agents:
            results.append({'Step': step, 'AgentID': a.agent_id, 'Location': a.location, 'Wealth': a.wealth})

out_df = pd.DataFrame(results)
out_df.to_csv('/home/hmid/ssan-data/mesa_output_weighted.csv', index=False)
print(f"Simulation complete. Saved {len(out_df)} agent state records.")

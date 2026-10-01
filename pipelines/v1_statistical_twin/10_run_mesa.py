import random
import json
import networkx as nx
import pandas as pd
import numpy as np

with open('/home/hmid/ssan-data/mesa_agents.json') as f:
    agents_data = json.load(f)
edges_df = pd.read_csv('/home/hmid/ssan-data/pykeen_edges.tsv', sep='\t', names=['head', 'relation', 'tail'])

G = nx.DiGraph()
for _, row in edges_df.iterrows():
    G.add_edge(row['head'], row['tail'])

class Agent:
    def __init__(self, agent_id, location, wealth, weight):
        self.agent_id = agent_id
        self.location = location
        self.wealth = wealth
        self.weight = weight

agents = [Agent(a['agent_id'], a['location'], a['wealth'], a['weight']) for a in agents_data]
print(f"Initializing pure Python model with {len(agents)} agents...")

results = []
print("Running 20 simulation steps...")
for step in range(20):
    random.shuffle(agents)
    for a in agents:
        a.wealth += np.random.normal(0, 0.5)
        if a.location in G.nodes and len(list(G.successors(a.location))) > 0:
            a.location = random.choice(list(G.successors(a.location)))
            
    if step == 19:
        for a in agents:
            results.append({'Step': step, 'AgentID': a.agent_id, 'Location': a.location, 'Wealth': a.wealth})

out_df = pd.DataFrame(results)
out_df.to_csv('/home/hmid/ssan-data/mesa_output.csv', index=False)
print(f"Simulation complete. Saved {len(out_df)} agent state records.")

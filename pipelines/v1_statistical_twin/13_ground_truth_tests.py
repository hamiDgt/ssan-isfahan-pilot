import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
mesa = pd.read_csv('/home/hmid/ssan-data/mesa_output.csv')
latent = pd.read_parquet('/home/hmid/ssan-data/latent_vectors.parquet')
val = pd.read_parquet('/home/hmid/ssan-data/validation_report.parquet')

# Test 1: Wealth Hotspots
wealth_caps = caps[caps['final_id'].isin(val['final_id'])].merge(val[['final_id', 'final_wealth']], on='final_id')
top_wealth = wealth_caps.nlargest(10, 'final_wealth')[['final_id', 'center_lat', 'center_lon', 'final_wealth']]
top_wealth.to_csv('/home/hmid/ssan-data/test1_wealth_hotspots.csv', index=False)
print("Test 1: Top 10 Wealth Hotspots generated.")

# Test 2: Agent Aggregation
final_locations = mesa.groupby('Location').size().reset_index(name='agent_count')
agent_caps = caps.merge(final_locations, left_on='final_id', right_on='Location', how='inner')
top_agents = agent_caps.nlargest(5, 'agent_count')[['final_id', 'center_lat', 'center_lon', 'agent_count']]
top_agents.to_csv('/home/hmid/ssan-data/test2_agent_hubs.csv', index=False)
print("Test 2: Top 5 Agent Hubs generated.")

# Test 3: Latent Neighborhoods
anchor_id = caps.loc[caps['gss'].idxmax(), 'final_id']
anchor_vec = latent[latent['h3_index'] == anchor_id].drop(columns=['h3_index']).values
latent_vecs = latent.set_index('h3_index')
sims = cosine_similarity(anchor_vec, latent_vecs.values)[0]
latent_vecs['similarity'] = sims
top_neighbors = latent_vecs.nlargest(6, 'similarity').reset_index()
top_neighbors = top_neighbors.merge(caps[['final_id', 'center_lat', 'center_lon']], left_on='h3_index', right_on='final_id')
top_neighbors.to_csv('/home/hmid/ssan-data/test3_latent_neighbors.csv', index=False)
print("Test 3: Top 5 Latent Neighbors generated.")

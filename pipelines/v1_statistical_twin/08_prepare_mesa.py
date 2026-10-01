import pandas as pd

iss = pd.read_parquet('/home/hmid/ssan-data/iss_cells_d6.parquet')
agents = iss[['iss_id', 'h3_index', 'age', 'wealth_proxy', 'expansion_weight']]
agents.columns = ['agent_id', 'location', 'age', 'wealth', 'weight']
agents.to_json('/home/hmid/ssan-data/mesa_agents.json', orient='records', indent=2)
print(f"Wrote {len(agents)} agents for Mesa.")

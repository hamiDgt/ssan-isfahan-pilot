import pandas as pd

mesa = pd.read_csv('/home/hmid/ssan-data/mesa_output_weighted.csv')
caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')

crowd = mesa.groupby('Location').size().reset_index(name='agent_count')
crowd = crowd.merge(caps[['final_id', 'center_lat', 'center_lon']], left_on='Location', right_on='final_id')
crowd['center_lat'] = crowd['center_lat'].round(5)
crowd['center_lon'] = crowd['center_lon'].round(5)
top = crowd.nlargest(10, 'agent_count')[['center_lat', 'center_lon', 'agent_count']]
print("=== WEIGHTED PLANNER TEST: Top 10 Crowd Densities ===")
print(top.to_string(index=False))

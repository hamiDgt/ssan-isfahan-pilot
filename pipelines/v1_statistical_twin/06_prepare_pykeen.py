import pandas as pd
import os

caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')

if not os.path.exists('/home/hmid/ssan-data/pykeen_edges.tsv'):
    raise FileNotFoundError("pykeen_edges.tsv not found. Script 05 failed.")

features = caps[['final_id', 'support', 'gss', 'resolution', 'mean_age', 'mean_wealth']]
features.columns = ['node_id', 'f1', 'f2', 'f3', 'f4', 'f5']
features.to_csv('/home/hmid/ssan-data/pykeen_nodes.tsv', sep='\t', index=False)
print(f"Wrote {len(features)} node features. Edges already prepared by script 05.")

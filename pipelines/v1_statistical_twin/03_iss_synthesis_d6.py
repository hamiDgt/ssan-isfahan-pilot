import pandas as pd
import numpy as np

np.random.seed(42)
df = pd.read_parquet('/home/hmid/ssan-data/d6_silver_calibrated.parquet')

TARGET_ISS = 15000
total_pop = df['population'].sum()

df['cell_share'] = df['population'] / total_pop
df['target_cells'] = (df['cell_share'] * TARGET_ISS).round(0).astype(int)
df.loc[df['population'] > 0, 'target_cells'] = df.loc[df['population'] > 0, 'target_cells'].clip(1)

iss_records = []
for _, row in df.iterrows():
    n = int(row['target_cells'])
    if n > 0:
        ages = np.random.normal(30, 15, n).clip(0, 100).astype(int)
        wealth = np.random.normal(row['radiance'], 5, n).clip(0, 63)
        weight = row['population'] / n
        
        for i in range(n):
            iss_records.append({
                'iss_id': f"ISS_{row['h3_index']}_{i}",
                'h3_index': row['h3_index'],
                'age': int(ages[i]),
                'wealth_proxy': float(wealth[i]),
                'expansion_weight': float(weight)
            })

iss_df = pd.DataFrame(iss_records)
iss_df.to_parquet('/home/hmid/ssan-data/iss_cells_d6.parquet', index=False)
print(f"Synthesized {len(iss_df)} ISS cells for District 6.")

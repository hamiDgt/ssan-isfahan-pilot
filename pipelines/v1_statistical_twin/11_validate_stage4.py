import pandas as pd

caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
mesa = pd.read_csv('/home/hmid/ssan-data/mesa_output.csv')

final_state = mesa.groupby('Location')['Wealth'].mean().reset_index()
final_state.columns = ['h3_index', 'final_wealth']

val_df = caps.merge(final_state, left_on='final_id', right_on='h3_index', how='inner')
val_df = val_df[['final_id', 'support', 'gss', 'mean_wealth', 'final_wealth']]

corr = val_df['mean_wealth'].corr(val_df['final_wealth'])
print(f"Correlation between initial radiance and final wealth: {corr:.3f}")
print(f"Validated {len(val_df)} capsules.")

val_df.to_parquet('/home/hmid/ssan-data/validation_report.parquet', index=False)

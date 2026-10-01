import pandas as pd
import h3

silver = pd.read_parquet('/home/hmid/ssan-data/d6_silver_calibrated.parquet')

try:
    gdelt = pd.read_csv('/home/hmid/ssan-data/gdelt_iran_7days.csv', sep='\t', dtype=str)
    gdelt['lat'] = pd.to_numeric(gdelt['ActionGeo_Lat'], errors='coerce')
    gdelt['lon'] = pd.to_numeric(gdelt['ActionGeo_Long'], errors='coerce')
    gdelt = gdelt.dropna(subset=['lat', 'lon'])
    gdelt['h3_index'] = [h3.latlng_to_cell(lat, lon, 9) for lat, lon in zip(gdelt['lat'], gdelt['lon'])]
    gdelt_agg = gdelt.groupby('h3_index').size().reset_index(name='event_count')
    print(f"Mapped {len(gdelt_agg)} hexagons with real GDELT events.")
except Exception as e:
    print(f"GDELT parse failed: {e}")
    gdelt_agg = pd.DataFrame(columns=['h3_index', 'event_count'])

silver = silver.merge(gdelt_agg, on='h3_index', how='left')
silver['event_count'] = silver['event_count'].fillna(0).astype(int)
silver['raw_gss'] = (silver['radiance'] * 0.5) + (silver['event_count'] * 10.0)

def get_neighbor_avg(row, df_dict):
    neighbors = h3.grid_ring(row['h3_index'], 1)
    scores = [df_dict.get(n, 0) for n in neighbors]
    return sum(scores) / len(scores) if scores else 0.0

gss_dict = dict(zip(silver['h3_index'], silver['raw_gss']))
silver['neighbor_gss'] = silver.apply(lambda row: get_neighbor_avg(row, gss_dict), axis=1)
silver['gss_context'] = (silver['raw_gss'] * 0.7) + (silver['neighbor_gss'] * 0.3)

silver.to_parquet('/home/hmid/ssan-data/d6_gss_context.parquet', index=False)
print(f"Built GSS context for {len(silver)} hexagons.")

import pandas as pd, h3

caps = pd.read_parquet('/home/hmid/ssan-data/capsules_d6.parquet')
silver = pd.read_parquet('/home/hmid/ssan-data/silver_full.parquet')

bbox = (32.5416814, 51.6627253, 32.6446693, 51.7650088)
s = silver[(silver.lat >= bbox[0]) & (silver.lon >= bbox[1]) & (silver.lat <= bbox[2]) & (silver.lon <= bbox[3])]
s = s[s.category.isin(['shop', 'amenity'])]
s = s.copy()
s['hex10'] = [h3.latlng_to_cell(a, b, 10) for a, b in zip(s.lat, s.lon)]
supply = s.groupby('hex10').size().reset_index(name='shops')

m = caps.merge(supply, left_on='final_id', right_on='hex10', how='left')
m['shops'] = m['shops'].fillna(0)
m['opportunity'] = m['support'] / (m['shops'] + 1)
top = m.nlargest(10, 'opportunity')[['center_lat', 'center_lon', 'support', 'shops']]
top['center_lat'] = top['center_lat'].round(5)
top['center_lon'] = top['center_lon'].round(5)
print(top.to_string(index=False))

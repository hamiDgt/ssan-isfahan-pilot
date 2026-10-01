import rasterio, numpy as np, pandas as pd, h3, json
from rasterio.windows import from_bounds
from shapely.geometry import Polygon, Point

# 1. Load Boundary Polygon safely
lats, lons = [], []
with open('/home/hmid/ssan-data/osm/district6_boundary.json') as f:
    data = json.load(f)
for e in data['elements']:
    if 'lat' in e: lats.append(e['lat']); lons.append(e['lon'])
    if 'geometry' in e:
        for pt in e['geometry']: lats.append(pt['lat']); lons.append(pt['lon'])
    if 'members' in e:
        for m in e['members']:
            if 'lat' in m: lats.append(m['lat']); lons.append(m['lon'])
            if 'geometry' in m:
                for pt in m['geometry']: lats.append(pt['lat']); lons.append(pt['lon'])

poly = Polygon(zip(lons, lats))
bbox = poly.bounds

# 2. Extract VIIRS Radiance
print("Reading VIIRS window...")
with rasterio.open('/home/hmid/ssan-data/worldpop/SVDNB_npp_20260601-20260630_global_vcmcfg_v10_c202607102200.avg_rade9h.tif') as src:
    window = from_bounds(*bbox, transform=src.transform)
    data_viirs = src.read(1, window=window)
    win_transform = src.window_transform(window)

rows, cols = data_viirs.shape
ys, xs = np.meshgrid(np.arange(rows), np.arange(cols), indexing='ij')
lons_pix, lats_pix = rasterio.transform.xy(win_transform, ys.ravel(), xs.ravel())
vals = data_viirs.ravel()

# 3. Filter points strictly inside the exact polygon
print("Filtering pixels inside polygon...")
mask = (vals > 0) & np.array([poly.contains(Point(lon, lat)) for lon, lat in zip(lons_pix, lats_pix)])
df_nl = pd.DataFrame({'lat': np.array(lats_pix)[mask], 'lon': np.array(lons_pix)[mask], 'radiance': vals[mask]})
df_nl['h3_index'] = [h3.latlng_to_cell(lat, lon, 9) for lat, lon in zip(df_nl['lat'], df_nl['lon'])]
nl = df_nl.groupby('h3_index')['radiance'].mean().reset_index()
print(f"Nightlight mapped to {len(nl)} hexagons.")

# 4. Process Buildings for Population Calibration
with open('/home/hmid/ssan-data/osm/d6_buildings.json') as f:
    bldg = json.load(f)
b_rows = [{'lat': e['center']['lat'], 'lon': e['center']['lon']} for e in bldg['elements'] if 'center' in e]
df_b = pd.DataFrame(b_rows)
df_b['h3_index'] = [h3.latlng_to_cell(lat, lon, 9) for lat, lon in zip(df_b['lat'], df_b['lon'])]
bldg_count = df_b.groupby('h3_index').size().reset_index(name='building_count')

# 5. Calibrate to exactly 112,129
TARGET_POP = 112129
total_bldg = bldg_count['building_count'].sum()
bldg_count['population'] = (bldg_count['building_count'] / total_bldg * TARGET_POP).round(0).astype(int)

# Adjust rounding errors
diff = TARGET_POP - bldg_count['population'].sum()
bldg_count.loc[bldg_count['building_count'].idxmax(), 'population'] += diff

final_d6 = bldg_count.merge(nl, on='h3_index', how='left').fillna(0.0)
final_d6.to_parquet('/home/hmid/ssan-data/d6_silver_calibrated.parquet', index=False)
print(f"Calibrated population: {final_d6['population'].sum()} across {len(final_d6)} hexagons.")

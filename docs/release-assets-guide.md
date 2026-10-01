# Release Assets Guide

The code repository stays under 50MB.
The heavy data files live in the GitHub release.
The NASA VIIRS sensor file is too large for GitHub.
You must download the nightlight file manually.

## Manual Download: NASA VIIRS
1. Go to the EOG Data portal: https://eogdata.mines.edu/products/vnl/
2. Create a free account and log in.
3. Download the monthly composite for your target date.
4. Place the `.tif` file in `~/ssan-data/worldpop/`.

## Release Assets
Download these files from the GitHub release.
Place them in your local `~/ssan-data/` directory.

1. `silver_full.parquet` (City-wide amenities)
2. `gdelt_iran_7days.csv` (Seven-day event log)
3. `osm_anchors.zip` (Spatial boundary and buildings)

# SSaN Isfahan Pilot

An analytical digital twin of Isfahan Municipality District 6.
The pilot proves the Spatial Social Agent Network architecture.
The model uses open data and local geographic validation.

## Core Concepts

A capsule is an H3 resolution-10 hexagon.
An ISS cell is one synthetic person.
Each person carries age, a wealth proxy, and a census weight.
The GSS cell holds macro context from nightlight and events.
The reliability cell holds conformal confidence bounds.
PyKEEN learns the latent geometry of the capsule graph.
Movement follows a gravity model on a street-weighted graph.
A person-to-person tie network completes the social layer.

## Repository Layout

pipelines/v1_statistical_twin   static calibration, PyKEEN, MAPIE, random walk
pipelines/v2_mobility_twin       residential filter, street weights, gravity model
pipelines/v3_social_twin          person network, nightlight layer, living map
shared                            SQL exports and the OSM download helper
docs                              Methodology, lessons learned, and worklogs

## Setup

1. Create a Python virtual environment.
2. Run `pip install -r requirements.txt`.
3. Run `shared/download_osm.sh` to fetch the OSM anchors.
4. Download the required release assets from the GitHub Releases page.
5. Place the assets in your local `~/ssan-data/` directory.
6. Run the pipeline scripts in numerical order.

## Release Assets

The code repository stays under 50MB.
The heavy data files live in the GitHub Releases.
Download these files and place them in `~/ssan-data/`:

1. **NASA VIIRS nightlight sensor** (Download manually from EOG Data portal, see docs/release-assets-guide.md)
2. `silver_full.parquet` (City-wide amenities)
3. `gdelt_iran_7days.csv` (Seven-day event log)
4. `osm_anchors.zip` (Spatial boundary and buildings)
5. `isfahan_twin_v3.html` (Final visual output)

## Validation Results

The model recovers real urban structures.
Wealth hotspots match the affluent Mardavij neighborhood accurately.
Latent neighbors share real socioeconomic characteristics.
Investor points sit in real underserved residential pockets.
South corridors match the Sepahan Shahr and City Center flows.
Mardavij and City Center bottlenecks match real choke points.
The model isolates the quiet Kuy-e Sepahan residential pockets.

## Known Limitations

Ties are rule-based, not surveyed.
Age has no spatial variation.
Wealth uses nightlight as an income proxy.
The twin is analytical, not operational.
The model lacks real temporal telemetry.

## Documentation

Read `docs/methodology.md` for the scientific foundation.
Read `docs/lessons-learned.md` for the engineering truths.
Read `docs/worklog.md` for the project phases.

## Citation

If you use this software, please cite it using the `CITATION.cff` file.

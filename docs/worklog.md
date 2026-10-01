# Worklog

The project progressed through five distinct phases.
Each phase built upon the previous spatial foundation.

## Phase One: Data Lake and Calibration
The team ingested VIIRS nightlight and GDELT events.
The team downloaded OpenStreetMap building footprints.
The team calibrated 112,129 population to H3 resolution nine.
The team synthesized the initial statistical cells.

## Phase Two: Graph and Latent Space
The team built the spatial capsule graph.
The team trained TransE embeddings with PyKEEN.
The team computed conformal prediction bounds.
The team exported the latent vectors to SQL.

## Phase Three: Mobility and Gravity
The team filtered non-residential buildings.
The team integrated the OSMnx street network.
The team calculated real street distance weights.
The team implemented the gravity movement model.
The team capped attractor strengths to balance zones.

## Phase Four: Ground Truth Validation
The team tested the model against local Isfahan geography.
The team validated wealth hotspots in Mardavij.
The team validated emergency bottlenecks at City Center.
The team identified micro-clusters in Kuy-e Sepahan.
The team refined the gravity decay exponent.

## Phase Five: Social Twin and Visualization
The team built the person-to-person network.
The team assigned agents to real residential buildings.
The team generated the living map with street polylines.
The team overlaid the real VIIRS nightlight polygons.

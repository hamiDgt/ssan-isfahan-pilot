# Methodology

The Spatial Social Agent Network combines three scientific methods.
Traditional agent models use synthetic grids.
This model uses real geographic anchors.

## The Spatial Foundation
The model uses the H3 Discrete Global Grid System.
Hexagons preserve area and topology better than square grids.
The base resolution is ten.
Each hexagon represents a specific physical place.
A capsule is a hexagon containing residential buildings.

## The Data Fusion
The model fuses three open data layers.
The first layer is OpenStreetMap building footprints.
The second layer is NASA VIIRS nighttime radiance.
The third layer is GDELT global event data.
The model filters out industrial and commercial buildings.
This filter prevents false population peaks.

## The Calibration
The model calibrates synthetic agents to real census data.
The target population is 112,129 residents.
The script counts residential buildings in each hexagon.
The script distributes the population proportionally.
The sum of agent weights equals the exact census total.

## The Latent Geometry
The model uses Graph Neural Networks for spatial embedding.
The TransE algorithm trains on the capsule neighborhood graph.
The algorithm embeds each capsule into a 64-dimensional vector space.
Similar vectors represent similar urban structures.

## The Uncertainty Quantification
The model uses Conformal Prediction for reliability bounds.
The method calculates a 90 percent confidence interval.
The interval measures the statistical certainty of the spatial context.
This prevents the model from hallucinating false precision.

## The Movement Dynamics
The model replaces random walks with a gravity rule.
Agents move toward real commercial attractors.
The movement force decays with real street distance.
The model uses OSMnx to calculate physical walking friction.
Agents follow the shortest physical paths.

## The Social Network
The model builds person-to-person ties from spatial rules.
Shared residential buildings create strong residence ties.
Shared daytime attractors create activity ties.
Similar age and wealth in adjacent capsules create homophily ties.
Label propagation discovers social communities from these ties.

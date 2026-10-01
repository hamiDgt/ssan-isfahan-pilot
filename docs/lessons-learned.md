# Lessons Learned

The pilot phase revealed critical truths about urban modeling.
Data quality dictates model success.
Architecture alone cannot fix bad spatial proxies.

## Geographic Validation
Statistical metrics are insufficient for digital twins.
Ground truth requires local geographic validation.
The model successfully recovered the affluent Mardavij neighborhood.
The model identified the Isfahan City Center as a major bottleneck.
The model isolated the quiet Kuy-e Sepahan residential pockets.
Statistical correlation cannot replace local expert judgment.

## Movement Dynamics
Random walks fail transit and emergency tests.
Agents must follow real physical friction.
The gravity model with capped attractors succeeds.
Capping attractor strength prevents one mall from swallowing the district.
Distance decay forces agents to use intermediate corridors.

## Data Engineering
OpenStreetMap tags require strict filtering.
Industrial tags create false population peaks.
Public Overpass APIs enforce strict rate limits.
Local caching is mandatory for reproducible pipelines.
Hard dependencies on specific library versions break over time.
Pure Python logic for core loops ensures longevity.

## Model Weaknesses
The social ties are synthetic rules.
The model lacks real temporal telemetry.
The age distribution lacks spatial variation.
The wealth proxy relies entirely on nightlight radiance.
The twin is analytical rather than operational.

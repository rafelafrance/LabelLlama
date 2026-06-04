---
name: habitat
description: Extract the habitat, environment, or ecological setting where the specimen was collected. This describes the physical conditions and ecological context, not the geographic location
---

# Prompt habitat

`habitat` (str): Extract the habitat, environment, or ecological setting where the specimen was collected. This describes the physical conditions and ecological context, not the geographic location.

✅ Include:
- Substrate and soil type: 'dry sand', 'loamy soil', 'rocky outcrop', 'calcareous rock', 'peat'
- Vegetation type and structure: 'open grassland', 'mixed forest', 'shrubland', 'pine savanna', 'dense canopy'
- Hydrological conditions: 'wetland', 'stream bank', 'riparian zone', 'marsh', 'floodplain', 'spring seep'
- Disturbance and land use: 'roadside', 'old field', 'disturbed ground', 'agricultural edge', 'urban park'
- Life zones and biomes: 'desert', 'prairie', 'alpine meadow', 'tundra', 'cloud forest'
- Microhabitats: 'under rotting log', 'in leaf litter', 'on tree trunk', 'under stones', 'in crevice'
- Multiple or compound habitats joined by commas or conjunctions

❌ DO NOT include:
- Associated taxa or host plants — those belong in `associatedTaxa`
- Place names, geographic features, or road names — those belong in `locality`
- Details about the specimen itself (e.g., height, color, flower/fruit status, developmental traits)
- Collection methods or equipment (e.g., 'light trap', 'sweep net')
- Elevation or climate data — those belong in `elevationValues` or `verbatimElevation`

Normalization: Preserve the text exactly as written — do not standardize ecological terms, expand abbreviations, or reorder phrases. If multiple habitats are listed, include all of them. If no habitat information is present, return an empty string.

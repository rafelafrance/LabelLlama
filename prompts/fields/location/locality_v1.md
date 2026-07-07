---
name: locality
description: Extract the locality — the specific place or geographic description where the specimen was collected. This describes the ground-level location, independent of higher administrative divisions or coordinates
module: llama/fields/location/locality.py
---

# Prompt locality

`locality` (str): Extract the locality — the specific place or geographic description where the specimen was collected. This describes the ground-level location, independent of higher administrative divisions or coordinates.

✅ Include:
- Place names and geographic features: 'Springfield', 'Mt. Hood', 'Cedar Creek', 'Great Salt Lake'
- Distances and directions from landmarks: '10 km NW of Springfield', '2 miles south of Highway 101'
- Road names, trails, and routes: 'along I-95', 'Forest Road 12', 'Blue Trail'
- Field-level descriptions and grid references: 'Plot 4A', 'Quadrat 12', 'Section 14'
- Multiple or compound localities joined by commas or conjunctions: 'near river, base of cliff'

❌ DO NOT include:
- Higher administrative divisions: country, state/province, county, municipality — those have their own fields
- Coordinates: decimal degrees, DMS, TRS, UTM — those belong in `verbatimLatitude`/`verbatimLongitude`
- Elevation or altitude: '1500 m', 'elev. 2000 ft' — those belong in `elevationValues`
- Habitat descriptions: 'pine forest', 'wetland', 'grassland', 'under rotting log' — those belong in `habitat`
- Associated taxa or host plants: 'on Quercus alba', 'parasitic on Drosophila' — those belong in `associatedTaxa`
- Collection methods or equipment: 'light trap', 'pitfall trap', 'sweep net' — unless part of the geographic description

Normalization: Preserve the text exactly as written — do not abbreviate place names, expand acronyms, or reorder phrases. If multiple localities are listed, include all of them. If no locality is present, return an empty string.

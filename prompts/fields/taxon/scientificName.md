---
name: scientificName
description: Extract the scientific name of the specimen at the species level. This is the primary taxonomic name used to identify the organism
---

# scientificName

`scientificName` (str): Extract the scientific name of the specimen at the species level. This is the primary taxonomic name used to identify the organism.

✅ Include:
- Binomial names formatted as 'Genus species' (e.g., 'Canis lupus', 'Drosophila melanogaster', 'Salix exigua')
- Genus name alone if identified only to genus level (e.g., 'Quercus', 'Aedes')
- Unidentified species notations such as 'sp.', 'spp.', 'sp. nov.' (e.g., 'Canis sp.')
- Comparison indicators if present: 'aff.', 'cf.' (e.g., 'Pinus aff. strobus')
- Hybrid symbol '×' if present (e.g., '×Rhododendron', 'Quercus × gussonei')

❌ DO NOT include:
- Infraspecific ranks (subspecies, varieties, forms) — those belong in `infraspecificEpithet` (e.g., from 'Canis lupus baileyi' return 'Canis lupus', not 'Canis lupus baileyi')
- Authorship citations (e.g., 'L.', 'Smith & Jones', '(Bartlett) Fernald') — those belong in `scientificNameAuthorship`
- Subgenus names (e.g., from 'Aedes (Finlaya) aegypti' return 'Aedes aegypti', not 'Aedes (Finlaya) aegypti')
- Higher taxonomic ranks (family, order) or common/vernacular names
- Synonymy notes, alternative names, or identification qualifiers like 'det. by', 'id.'

Normalization: Capitalize the genus and lowercase the specific epithet (e.g., 'CANIS lupus' → 'Canis lupus'). Preserve the hybrid symbol '×' if present. There will always be a scientific name.

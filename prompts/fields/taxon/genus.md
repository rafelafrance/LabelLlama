---
name: genus
description: Extract the taxonomic genus of the specimen (e.g., 'Canis', 'Salix', 'Agoseris', 'Drosophila')
---

# Prompt genus

`genus` (str): Extract the taxonomic genus of the specimen (e.g., 'Canis', 'Salix', 'Agoseris', 'Drosophila'). The genus is the first component of the scientific name and is typically capitalized.

✅ Include:
- The genus name alone (e.g., from 'Canis lupus' extract 'Canis')
- Hybrid symbol '×' if it precedes the genus (e.g., '×Rhododendron')
- Genus from the primary (most specific) identification when multiple identifications are present

❌ DO NOT include:
- Specific epithet — that belongs in `specificEpithet` (e.g., from 'Canis lupus' extract 'Canis', not 'Canis lupus')
- Infraspecific epithets (subspecies, varieties, forms) — those belong in `infraspecificEpithet`
- Subgenus names — those belong in `subgenus` (e.g., from 'Aedes (Finlaya) aegypti' extract 'Aedes', not 'Finlaya')
- Authorship citations (e.g., 'L.', 'Smith & Jones') — those belong in `scientificNameAuthorship`
- Higher taxonomic ranks (family, order) — those belong in `family` or higher fields
- Labels or prefixes (e.g., 'gen.', 'Genus:') — extract only the genus name itself
- Identification qualifiers (e.g., 'det. by', 'id.', 'aff.', 'cf.')

Normalization: Capitalize the first letter of the genus name. Do not alter the spelling. If the genus appears with a label (e.g., 'gen. Quercus'), extract only 'Quercus'.

Examples:
- 'Canis lupus' → 'Canis'
- 'Aedes (Finlaya) aegypti' → 'Aedes'
- '×Rhododendron' → '×Rhododendron'
- 'Quercus alba L.' → 'Quercus'
- 'gen. Salix' → 'Salix'
- 'Salix (Salix) exigua' → 'Salix'
- 'Drosophila melanogaster subsp. simulans' → 'Drosophila'
- 'Canis lupus baileyi' → 'Canis'

If no genus is stated, return an empty string.

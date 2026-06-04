---
name: specificEpithet
description: Extract the taxonomic specific epithet of the specimen (e.g., 'exigua', 'lupus', 'domesticus'). The specific epithet is the second component of the binomial scientific name, following the genus
module: llama/fields/taxon/specificEpithet.py
---

# Prompt specificEpithet

`specificEpithet` (str): Extract the taxonomic specific epithet of the specimen (e.g., 'exigua', 'lupus', 'domesticus'). The specific epithet is the second component of the binomial scientific name, following the genus.

✅ Include:
- The specific epithet alone (e.g., from 'Canis lupus' extract 'lupus')
- Epithets from trinomial names (e.g., from 'Canis lupus baileyi' extract 'lupus', not 'baileyi')
- Hybrid epithets containing '×' (e.g., from 'Quercus × gussonei' extract '× gussonei')

❌ DO NOT include:
- The genus name — that belongs in `genus` (e.g., from 'Canis lupus' extract 'lupus', not 'Canis lupus')
- Infraspecific epithets (subspecies, varieties, forms) — those belong in `infraspecificEpithet`
- Authorship citations (e.g., 'L.', 'Smith & Jones', '(Michx.) Torr.') — those belong in `scientificNameAuthorship`
- Subgenus names — those belong in `subgenus`
- Higher taxonomic ranks (family, order)
- Labels or prefixes (e.g., 'sp.', 'species:') — extract only the epithet itself
- Identification qualifiers (e.g., 'det. by', 'id.', 'aff.', 'cf.')
- Unidentified species notations ('sp.', 'spp.', 'sp. nov.') — these are not epithets

Normalization: Return the epithet in lowercase. Strip the genus name, authorship, and any rank indicators. Do not alter the spelling.

Examples:
- 'Canis lupus' → 'lupus'
- 'Drosophila melanogaster' → 'melanogaster'
- 'Salix exigua' → 'exigua'
- 'Canis lupus baileyi' → 'lupus'
- 'Quercus alba L.' → 'alba'
- 'Aedes (Finlaya) aegypti' → 'aegypti'
- 'Quercus alba L. var. latifolia (Michx.) Torr.' → 'alba'
- 'Quercus sp.' → '' ('sp.' is not an epithet)
- 'Pinus aff. strobus' → 'strobus'
- 'Salix (Salix) exigua Sm.' → 'exigua'

If no specific epithet is stated, return an empty string.

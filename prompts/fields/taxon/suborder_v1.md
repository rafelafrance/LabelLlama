---
name: suborder
description: Extract the taxonomic suborder of the specimen (e.g., 'Violineae', 'Cucurbitineae', 'Heterodontina'). The suborder ranks between order and family
module: llama/fields/taxon/suborder.py
---

# Prompt suborder

`suborder` (str): Extract the taxonomic suborder of the specimen (e.g., 'Violineae', 'Cucurbitineae', 'Heterodontina'). The suborder ranks between order and family. It is distinct from order (a higher rank) and family (a lower rank).

✅ Include:
- Suborder names with explicit labels (e.g., 'subord. Violineae', 'suborder Cucurbitineae')
- Botanical suborder names typically ending in '-ineae' (e.g., 'Violineae', 'Cucurbitineae', 'Rosineae')
- Zoological suborder names typically ending in '-ina' (e.g., 'Heterodontina', 'Lacertilia', 'Haplorhini')
- Suborder names appearing as standalone taxonomic names without labels

❌ DO NOT include:
- Order names (higher rank) — e.g., 'Rosales', 'Cucurbitales', 'Squamata'
- Family names (lower rank) — those belong in `family` (e.g., 'Rosaceae', 'Asteraceae')
- Subfamily names (lower rank) — e.g., 'Faboideae', 'Nepentoideae', 'Cicindelinae'
- Genus, specific epithet, or infraspecific names — those belong in their respective fields
- Authorship citations — those belong in `scientificNameAuthorship`
- Labels or prefixes (e.g., 'subord.', 'suborder:') — extract only the suborder name itself

Normalization: Capitalize the first letter of the suborder name. Do not alter the spelling. If the suborder name appears with a label (e.g., 'subord. Violineae'), extract only 'Violineae'.

Examples:
- 'Violineae' → 'Violineae'
- 'subord. Cucurbitineae' → 'Cucurbitineae'
- 'suborder Heterodontina' → 'Heterodontina'
- 'Rosales' → '' (this is an order, not a suborder)
- 'Rosaceae' → '' (this is a family, not a suborder)
- 'Faboideae' → '' (this is a subfamily, not a suborder)
- 'Cicindelinae' → '' (this is a subfamily, not a suborder)

If no suborder is stated, return an empty string.

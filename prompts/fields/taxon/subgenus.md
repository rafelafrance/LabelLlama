---
name: subgenus
description: Extract the taxonomic subgenus of the specimen (e.g., 'Finlaya', 'Leptalegia', 'Caninae'). The subgenus ranks between genus and species. It is commonly written in parentheses between the genus and the specific epithet, or with an explicit label
---

# subgenus

`subgenus` (str): Extract the taxonomic subgenus of the specimen (e.g., 'Finlaya', 'Leptalegia', 'Caninae'). The subgenus ranks between genus and species. It is commonly written in parentheses between the genus and the specific epithet, or with an explicit label.

✅ Include:
- Subgenus in parentheses (e.g., from 'Aedes (Finlaya) aegypti' extract 'Finlaya')
- Subgenus with explicit labels (e.g., 'subgen. Finlaya', 'subg. Leptalegia')
- Subgenus appearing without parentheses or labels if clearly indicated as such

❌ DO NOT include:
- The genus name — that belongs in `genus` (e.g., from 'Aedes (Finlaya) aegypti' extract 'Finlaya', not 'Aedes')
- The specific or infraspecific epithet — those belong in `specificEpithet` and `infraspecificEpithet`
- Authorship citations (e.g., 'L.', 'Smith & Jones') — those belong in `scientificNameAuthorship`
- Section or series names (lower ranks indicated by 'sect.', 'ser.', 'section', 'series')
- Higher taxonomic ranks (tribe, subfamily, family)
- Labels or prefixes (e.g., 'subgen.', 'subg.', 'subgenus:') — extract only the subgenus name itself
- The parentheses themselves — extract only the name inside

Normalization: Capitalize the first letter of the subgenus name. Strip all labels, parentheses, and authorship. Do not alter the spelling.

Examples:
- 'Aedes (Finlaya) aegypti' → 'Finlaya'
- 'Drosophila (Sophophora) melanogaster' → 'Sophophora'
- 'subgen. Caninae' → 'Caninae'
- 'subg. Leptalegia' → 'Leptalegia'
- 'Canis lupus L.' → '' (no subgenus stated)
- 'Salix (Salix) exigua' → 'Salix' (tautonymous subgenus, still extracted)
- 'Quercus sect. Cyclobalanopsis' → '' ('sect.' indicates section, not subgenus)
- 'Aedes (Finlaya) aegypti (Diptera)' → 'Finlaya' (family/order in parentheses is not subgenus)

If no subgenus is stated, return an empty string.

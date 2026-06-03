`family` (str): Extract the taxonomic family of the specimen (e.g., 'Rosaceae', 'Asteraceae', 'Fabaceae'). The family name is typically near the scientific name on the label, often preceded by a label like 'fam.' or 'Family:'.

✅ Include:
- Standard family names ending in '-aceae' (e.g., 'Rosaceae', 'Asteraceae', 'Fabaceae', 'Poaceae')
- Family names with explicit labels: 'fam. Rosaceae', 'Family: Asteraceae'
- Non-standard or older family endings (e.g., 'Rosidae', 'Compositae')
- Family names in any case as written on the label

❌ DO NOT include:
- Higher taxonomic ranks (order, class, division) — e.g., 'Rosales', 'Magnoliopsida'
- Lower taxonomic ranks (genus, species, subspecies) — those belong in `genus`, `specificEpithet`, `infraspecificEpithet`
- Authorship citations — those belong in `scientificNameAuthorship`
- Common or vernacular names — those belong in `vernacularName`
- Labels or prefixes (e.g., 'fam.', 'Family:') — extract only the family name itself

Normalization: Capitalize the first letter of the family name. Do not alter the spelling. If the family name appears with a label (e.g., 'fam. Rosaceae'), extract only 'Rosaceae'.

Examples:
- 'Rosaceae' → 'Rosaceae'
- 'fam. Asteraceae' → 'Asteraceae'
- 'Family: Fabaceae' → 'Fabaceae'
- 'Compositae' → 'Compositae' (older name, preserved as written)
- 'Rosales' → '' (this is an order, not a family)
- 'Quercus alba L. (Fagaceae)' → 'Fagaceae'

If no family is stated, return an empty string.

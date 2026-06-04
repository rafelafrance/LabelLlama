---
name: infraspecificEpithet
description: Extract the infraspecific epithet (subspecies, variety, or form name) from the scientific name
---

# Prompt

`infraspecificEpithet` (str): Extract the infraspecific epithet (subspecies, variety, or form name) from the scientific name. This is the third name after the genus and specific epithet.

✅ Include:
- Subspecies epithets (e.g., from 'Canis lupus baileyi' extract 'baileyi')
- Variety epithets (e.g., from 'Quercus alba var. latifolia' extract 'latifolia')
- Form epithets (e.g., from 'Salix exigua f. glabra' extract 'glabra')
- Infraspecific names without explicit rank indicators (e.g., 'Drosophila melanogaster simulans' → 'simulans')

❌ DO NOT include:
- Rank indicators ('subsp.', 'ssp.', 'var.', 'forma', 'f.') — extract only the epithet itself
- The genus or specific epithet — those belong in `genus` and `specificEpithet`
- Authorship citations (e.g., 'L.', 'Michx.') — those belong in `scientificNameAuthorship`
- Infraspecific authorship (e.g., from 'Quercus alba L. var. latifolia (Michx.) Torr.' extract 'latifolia', not '(Michx.) Torr.')
- Higher taxonomic ranks (family, order)
- Labels or prefixes (e.g., 'subspecies:', 'variety:') — extract only the epithet itself

Normalization: Return the epithet in lowercase. Strip all rank indicators and authorship. If the epithet appears with a label (e.g., 'var. latifolia'), extract only 'latifolia'.

Examples:
- 'Canis lupus baileyi' → 'baileyi'
- 'Quercus alba var. latifolia' → 'latifolia'
- 'Salix exigua subsp. montana' → 'montana'
- 'Drosophila melanogaster f. simulans' → 'simulans'
- 'Agoseris aurantiaca var. aurantiaca' → 'aurantiaca'
- 'Quercus alba L. var. latifolia (Michx.) Torr.' → 'latifolia'
- 'Canis lupus L.' → '' (no infraspecific rank)
- 'Salix exigua Sm.' → '' (no infraspecific rank)

If no infraspecific epithet is present, return an empty string.

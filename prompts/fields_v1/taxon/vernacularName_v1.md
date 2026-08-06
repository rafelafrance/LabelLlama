---
name: vernacularName
description: Extract the vernacular (common) name of the species collected
module: llama/fields/taxon/vernacularName.py
---

# Prompt vernacularName

`vernacularName` (str): Extract the vernacular (common) name of the species collected. Vernacular names are non-scientific names used locally, regionally, or in trade, often in English or other languages.

✅ Include:
- Standard common names: 'White Oak', 'Mountain Lion', 'California Poppy', 'Red-tailed Hawk'
- Regional, local, or slang names: 'gopher snake', 'prairie chicken', 'devil's claw'
- Indigenous or non-English names if present: 'cempasúchil', 'kauri', 'mañongo'
- Trade or market names: 'red snapper', 'king crab', 'wild rice'
- Names with hyphens, apostrophes, or special characters: 'Red-tailed Hawk', 'O'Malley's fern', 'Löwenmäulchen'

❌ DO NOT include:
- Scientific (Latin) names — those belong in `scientificName` (e.g., 'Quercus alba', 'Canis lupus')
- Taxonomic rank indicators or labels (e.g., 'common name:', 'vernacular:', 'nom. vulg.', 'local name:') — extract only the value
- Descriptive phrases that are not established common names (e.g., 'large brown moth', 'small white flower')
- Hybrid or cultivar designations mixed into the common name
- Multiple vernacular names — if several are listed, return only the primary or first one

Normalization: Preserve the name exactly as written — do not change capitalization, add/remove hyphens, or translate to another language. If no vernacular name is stated, return an empty string.

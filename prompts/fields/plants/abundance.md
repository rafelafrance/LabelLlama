---
name: abundance
description: Extract the abundance or frequency of the specimen at the collection site. This describes how common or rare the plant was where it was collected, not its conservation status or global rarity
---

# Prompt abundance

`abundance` (str): Extract the abundance or frequency of the specimen at the collection site. This describes how common or rare the plant was where it was collected, not its conservation status or global rarity.

✅ Include:
- Common abundance terms: 'common', 'abundant', 'frequent', 'usual', 'regular'
- Low abundance terms: 'rare', 'scarce', 'uncommon', 'infrequent', 'occasional', 'few', 'seldom'
- Distribution-based terms: 'scattered', 'sparse', 'local', 'patchy', 'isolated'
- High abundance terms: 'numerous', 'copious', 'dominant', 'profuse', 'massive'
- Quantitative abundance (e.g., '2 individuals', 'several plants', 'one specimen')
- Abundance relative to other species (e.g., 'most abundant species', 'co-dominant')

❌ DO NOT include:
- Conservation status indicators (e.g., 'endangered', 'threatened', 'extirpated', 'IUCN Red List') — these describe global/regional status, not local abundance
- Phenology terms (e.g., 'in flower', 'fruiting', 'dormant') — those belong in `lifeStage`
- Habitat descriptors that imply abundance without stating it (e.g., 'in dense forest', 'on rocky outcrop')
- Collection effort or method (e.g., 'collected in bulk', 'voucher specimen')
- Labels or prefixes (e.g., 'abundance:', 'freq.') — extract only the abundance term itself

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'numerous', do not change to 'abundant'). If quantitative, preserve the number and unit as written.

Examples:
- 'common' → 'common'
- 'abundant' → 'abundant'
- 'scattered' → 'scattered'
- 'rare' → 'rare'
- 'occasional' → 'occasional'
- 'numerous' → 'numerous'
- 'uncommon' → 'uncommon'
- 'few' → 'few'
- 'sparse' → 'sparse'
- 'dominant' → 'dominant'
- '2 individuals' → '2 individuals'
- 'endangered' → '' (conservation status, not local abundance)
- 'in flower' → '' (phenology, not abundance)
- 'in dense forest' → '' (habitat, not abundance)

If no abundance information is stated, return an empty string.

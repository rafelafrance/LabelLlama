---
name: flowersPresent
description: Determine whether the specimen has flowers present at the time of collection. This indicates the reproductive/phenological state of the plant
---

# Prompt

`flowersPresent` (bool): Determine whether the specimen has flowers present at the time of collection. This indicates the reproductive/phenological state of the plant.

✅ Return `true` if you find:
- Explicit flowering indicators: 'in flower', 'blooming', 'flowering', 'fl.', 'fls', 'flowers'
- Flower color descriptions (e.g., 'flowers white', 'pink blooms') — the mention of flower color implies flowers are present
- Combined reproductive states including flowers (e.g., 'flower and fruit', 'fl. and fr.', 'flowering and fruiting')

❌ Return `false` if:
- The specimen is explicitly described as not flowering (e.g., 'not in flower', 'no flowers', 'flowerless')
- Only vegetative parts are mentioned (e.g., 'vegetative', 'leafy', 'stem only')

Examples:
- 'in flower' → `true`
- 'blooming' → `true`
- 'fl.' → `true`
- 'flowers white' → `true` (flower color implies presence)
- 'flower and fruit' → `true`
- 'fl. and fr.' → `true`
- 'not in flower' → `false`
- 'no flowers' → `false`
- 'vegetative' → `false`
- 'in fruit' → `false` (fruit does not imply flowers)
- 'dormant' → `false`

If no information about flowers is stated, return an empty string.

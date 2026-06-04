---
name: fruitPresent
description: Determine whether the specimen has fruit present at the time of collection. This indicates the reproductive/phenological state of the plant
---

# Prompt

`fruitPresent` (bool): Determine whether the specimen has fruit present at the time of collection. This indicates the reproductive/phenological state of the plant.

✅ Return `true` if you find:
- Explicit fruiting indicators: 'in fruit', 'fruiting', 'fr.', 'frs', 'fruits'
- Fruit color descriptions (e.g., 'fruit red', 'black berries') — the mention of fruit color implies fruit is present
- Combined reproductive states including fruit (e.g., 'flower and fruit', 'fl. and fr.', 'flowering and fruiting')

❌ Return `false` if:
- The specimen is explicitly described as not fruiting (e.g., 'not in fruit', 'no fruit', 'fruitless')
- Only vegetative parts are mentioned (e.g., 'vegetative', 'leafy', 'stem only')

Examples:
- 'in fruit' → `true`
- 'fruiting' → `true`
- 'fr.' → `true`
- 'fruit red' → `true` (fruit color implies presence)
- 'flower and fruit' → `true`
- 'fl. and fr.' → `true`
- 'not in fruit' → `false`
- 'no fruit' → `false`
- 'vegetative' → `false`
- 'in flower' → `false` (flowers do not imply fruit)
- 'dormant' → `false`

If no information about fruit is stated, return an empty string.

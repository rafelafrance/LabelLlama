---
name: fruitColor
description: Extract the color(s) of the fruits of the specimen. This describes the visual appearance of the fruit (berries, capsules, nuts, drupes, etc.) at the time of collection or at maturity
---

# Prompt

`fruitColor` (str): Extract the color(s) of the fruits of the specimen. This describes the visual appearance of the fruit (berries, capsules, nuts, drupes, etc.) at the time of collection or at maturity.

✅ Include:
- Single colors (e.g., 'red', 'black', 'purple', 'green', 'brown', 'orange')
- Compound or gradient colors (e.g., 'reddish-brown', 'dark blue', 'yellowish-green')
- Mottled or variegated patterns (e.g., 'mottled red and white', 'striped yellow and green')
- Conditional or maturity-based colors (e.g., 'yellow when ripe', 'green turning red', 'purple at maturity')
- Multiple colors describing different fruit parts (e.g., 'red skin, white flesh')

❌ DO NOT include:
- Flower colors — those belong in `flowerColor` (e.g., 'white petals' is flower, not fruit)
- Leaf or stem colors — those belong in their respective fields
- Seed colors unless explicitly described as fruit color (e.g., 'seeds black' is not fruit color)
- Fruit size or shape descriptors (e.g., 'large berries', 'round fruit', 'clustered')
- Phenology or fruiting time (e.g., 'in fruit', 'fruiting in fall') — those belong in `lifeStage`
- Edibility or taste descriptors (e.g., 'sweet', 'bitter', 'edible') — these are not colors
- Labels or prefixes (e.g., 'fruit color:', 'berries:') — extract only the color description

Normalization: Extract only the color description. Strip size, shape, phenology, taste, and other non-color descriptors. Preserve the color text exactly as written — do not standardize synonyms or merge multiple colors.

Examples:
- 'red' → 'red'
- 'black' → 'black'
- 'purple' → 'purple'
- 'reddish-brown' → 'reddish-brown'
- 'yellow when ripe' → 'yellow when ripe'
- 'red skin, white flesh' → 'red skin, white flesh'
- 'mottled red and white' → 'mottled red and white'
- 'white petals' → '' (this is flower color, not fruit color)
- 'large red berries' → 'red' (strip size descriptor)
- 'in fruit, green' → 'green' (strip phenology descriptor)
- 'sweet orange fruit' → 'orange' (strip taste descriptor)
- 'seeds black' → '' (seed color is not fruit color)

If no fruit color is stated, return an empty string.

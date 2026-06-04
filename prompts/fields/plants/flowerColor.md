---
name: flowerColor
description: Extract the color(s) of the flowers of the specimen. This describes the visual appearance of the petals, sepals, or overall inflorescence at the time of collection
module: llama/fields/plants/flowerColor.py
---

# Prompt flowerColor

`flowerColor` (str): Extract the color(s) of the flowers of the specimen. This describes the visual appearance of the petals, sepals, or overall inflorescence at the time of collection.

✅ Include:
- Single colors (e.g., 'white', 'pink', 'yellow', 'purple', 'blue', 'red', 'cream')
- Compound or gradient colors (e.g., 'greenish-yellow', 'reddish-purple', 'bluish-white')
- Mottled or variegated patterns (e.g., 'mottled purple and white', 'striped red and yellow')
- Conditional colors (e.g., 'yellow when mature', 'pink fading to white', 'green turning red')
- Multiple colors describing different parts (e.g., 'white petals, yellow center')

❌ DO NOT include:
- Fruit colors — those belong in `fruitColor` (e.g., 'red berries' is fruit, not flower)
- Leaf or stem colors — those belong in their respective fields
- Scent or odor descriptors (e.g., 'fragrant', 'sweet-smelling', 'musty') — these are not colors
- Flower size or shape descriptors (e.g., 'large flowers', 'bell-shaped', 'clustered')
- Phenology or flowering time (e.g., 'in full bloom', 'late spring flowering') — those belong in `lifeStage`
- Conservation or rarity terms (e.g., 'rarely seen in red') — those belong in `abundance`
- Labels or prefixes (e.g., 'fl. color:', 'flowers:') — extract only the color description

Normalization: Extract only the color description. Strip scent, size, shape, phenology, and other non-color descriptors. Preserve the color text exactly as written — do not standardize synonyms or merge multiple colors.

Examples:
- 'white' → 'white'
- 'pink' → 'pink'
- 'yellow' → 'yellow'
- 'greenish-yellow' → 'greenish-yellow'
- 'mottled purple and white' → 'mottled purple and white'
- 'white petals, yellow center' → 'white petals, yellow center'
- 'pink fading to white' → 'pink fading to white'
- 'red berries' → '' (this is fruit color, not flower color)
- 'fragrant white flowers' → 'white' (strip scent descriptor)
- 'in full bloom, yellow' → 'yellow' (strip phenology descriptor)
- 'large bell-shaped flowers, purple' → 'purple' (strip size/shape descriptor)

If no flower color is stated, return an empty string.

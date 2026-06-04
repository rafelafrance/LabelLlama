---
name: plantHeight
description: Extract the overall height of the specimen or the plant as a whole
---

# Prompt

`plantHeight` (str): Extract the overall height of the specimen or the plant as a whole. This is a dimension describing the total vertical size of the plant, typically given as a number with units (e.g., '15 cm', '1.2 m', '3 ft', '2-5 m'). It is distinct from individual plant part sizes (leaf size, flower size, fruit size, etc.), which belong in `plantSizes`.

✅ Include:
- Explicit height values: '10 cm', '0.5-2 m', '15-30 cm tall', 'up to 3 m', 'ca. 50 cm', 'about 1 m'
- Height with descriptive qualifiers: 'tall', 'short', 'low', 'dwarf', 'giant', 'huge', 'minute', 'tiny' (when paired with or implying a measurement)
- Approximate/estimated height: 'ca.', 'approx.', 'about', 'circa', '±', '~', 'nearly', 'almost'
- Height ranges: '0.5-2 m', '10-30 cm', '1-3 ft'
- Height with context: '1.5 m tall', 'reaching 2 m', 'to 50 cm high', 'up to 3 m'
- Multiple height values (e.g., for different growth phases or parts of the same plant): keep as written

❌ DO NOT include:
- Individual plant part sizes — those belong in `plantSizes` (e.g., 'leaves 5 cm long', 'flowers 1 cm wide', 'fruit 3 mm diam', 'stem 2 cm thick')
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate', 'creeping')
- Woodiness — those belong in `woodiness` (e.g., 'woody', 'herbaceous')
- Life cycle — those belong in `lifeCycle` (e.g., 'annual', 'perennial')
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous')
- Developmental or phenological stage — those belong in `lifeStage` (e.g., 'seedling', 'flowering', 'dormant')
- Ecological life form — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic')
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Labels or prefixes (e.g., 'height:', 'ht.', 'size:') — extract only the measurement value itself, not the label

Note: When 'tall' or 'short' appears without a numeric value, include it only if it clearly describes the plant's height (e.g., 'a tall shrub' → 'tall'). When these words describe something else (e.g., 'tall grass habitat'), they belong in `habitat`. For measurements that mix overall height with part sizes (e.g., '1 m tall, leaves 5 cm'), extract only the overall height portion ('1 m tall').

Normalization: Preserve the text exactly as written, including units, ranges, approximations, and any qualifiers. Do not convert units (e.g., keep '3 ft' as '3 ft', do not change to '0.9 m'). Do not standardize abbreviations (e.g., keep 'ca.' or 'approx.' as written).

Examples:
- '15 cm' → '15 cm'
- '0.5-2 m' → '0.5-2 m'
- '15-30 cm tall' → '15-30 cm tall'
- 'up to 3 m' → 'up to 3 m'
- 'ca. 50 cm' → 'ca. 50 cm'
- '1.2 m' → '1.2 m'
- '3 ft' → '3 ft'
- 'reaching 2 m' → 'reaching 2 m'
- 'to 50 cm high' → 'to 50 cm high'
- 'about 1 m' → 'about 1 m'
- 'tall' → 'tall' (when clearly describing plant height)
- 'leaves 5 cm long' → '' (this is plant part size, not overall height)
- 'flowers 1 cm wide' → '' (this is plant part size, not overall height)
- 'stem 2 cm thick' → '' (this is plant part size, not overall height)
- 'fruit 3 mm diam' → '' (this is plant part size, not overall height)
- 'erect' → '' (this is habit, not height)
- 'climbing' → '' (this is habit, not height)
- 'woody' → '' (this is woodiness, not height)
- 'in forest' → '' (this is habitat, not height)

If no height information is stated, return an empty string.

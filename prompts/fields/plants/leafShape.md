---
name: leafShape
description: Extract the shape of the specimen's leaf. This describes the overall outline, form, or division pattern of the leaf blade
---

# Prompt leafShape

`leafShape` (str): Extract the shape of the specimen's leaf. This describes the overall outline, form, or division pattern of the leaf blade.

✅ Include:
- Basic blade shapes: 'elliptic', 'ovate', 'lanceolate', 'oblong', 'orbicular', 'linear', 'falcate', 'spatulate', 'obovate', 'rhombic', 'deltoid', 'cordate', 'reniform', 'sagittate', 'hastate'
- Compound/divided shapes: 'pinnate', 'palmate', 'bipinnate', 'trifoliate', 'dissected', 'lobed'
- General form descriptors: 'broad', 'narrow', 'elongated', 'lance-shaped'

❌ DO NOT include:
- Leaf margin (edge shape) — those belong in `leafMargin` (e.g., 'serrate', 'entire', 'crenate', 'toothed')
- Leaf duration or retention — those belong in `leafDuration` (e.g., 'deciduous', 'evergreen')
- Leaf texture or surface — those belong in their respective fields (e.g., 'smooth', 'rough', 'glandular', 'pubescent')
- Leaf venation or veins — those belong in their respective fields (e.g., 'pinnate-veined', 'parallel-veined', 'reticulate')
- Leaf color or arrangement — those belong in their respective fields (e.g., 'alternate', 'opposite', 'whorled', 'green')
- Habitat or environmental descriptors — those belong in `habitat`
- Labels or prefixes (e.g., 'leaf shape:', 'blade:', 'shape:') — extract only the shape term itself

Note: 'lobed', 'pinnate', and 'palmate' can describe both leaf shape and leaf margin or venation. When used to describe the overall leaf outline or division pattern, they are shape descriptors. When used to describe the edge (margin) or vein pattern, they belong in their respective fields. Use context to determine the correct field.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms. If multiple leaf shape terms are listed, keep them as they appear.

Examples:
- 'elliptic' → 'elliptic'
- 'ovate' → 'ovate'
- 'lanceolate' → 'lanceolate'
- 'cordate' → 'cordate'
- 'pinnate' → 'pinnate'
- 'palmate' → 'palmate'
- 'lobed' → 'lobed'
- 'ovate, acute' → 'ovate, acute'
- 'serrate' → '' (this is leaf margin, not shape)
- 'entire' → '' (this is leaf margin, not shape)
- 'deciduous' → '' (this is leaf duration, not shape)
- 'alternate' → '' (this is leaf arrangement, not shape)
- 'pubescent' → '' (this is leaf texture, not shape)
- 'pinnate-veined' → '' (this is leaf venation, not shape)

If no leaf shape information is stated, return an empty string.

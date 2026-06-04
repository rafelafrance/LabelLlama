---
name: leafMargin
description: Extract the description of the specimen's leaf margins (edge shape). This describes the physical appearance of the leaf border or edge
---

# leafMargin

`leafMargin` (str): Extract the description of the specimen's leaf margins (edge shape). This describes the physical appearance of the leaf border or edge.

✅ Include:
- Smooth edges: 'entire', 'smooth', 'plane'
- Toothed edges: 'serrate', 'serrulate', 'dentate', 'denticulate', 'toothed', 'crenate', 'crenulate', 'scalloped'
- Hairy/fringed edges: 'ciliate', 'ciliate-dentate', 'fringed', 'fimbriate'
- Wavy/irregular edges: 'undulate', 'sinuate', 'sinuate-dentate', 'repand'
- Deeply cut edges: 'lobed', 'incised', 'cut', 'pinnatifid', 'palmatifid'
- Compound/double margins: 'doubly serrate', 'biserrate', 'serrate-crenate'

❌ DO NOT include:
- Leaf shape or overall outline — those belong in `leafShape` (e.g., 'elliptic', 'ovate', 'lanceolate', 'cordate')
- Leaf duration or retention — those belong in `leafDuration` (e.g., 'deciduous', 'evergreen')
- Leaf texture or surface — those belong in their respective fields (e.g., 'smooth', 'rough', 'glandular')
- Leaf venation or veins — those belong in their respective fields (e.g., 'pinnate-veined', 'parallel-veined')
- Leaf color or arrangement — those belong in their respective fields (e.g., 'alternate', 'opposite', 'whorled')
- Habitat or environmental descriptors — those belong in `habitat`
- Labels or prefixes (e.g., 'margin:', 'edge:', 'leaf margin:') — extract only the margin term itself

Note: 'lobed' can describe both leaf shape and leaf margin. When used to describe deep cuts or indentations along the leaf edge, it is a margin descriptor. When used to describe the overall leaf outline, it is a shape descriptor. Use context to determine the correct field.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms. If multiple margin terms are listed, keep them as they appear.

Examples:
- 'serrate' → 'serrate'
- 'entire' → 'entire'
- 'crenate' → 'crenate'
- 'dentate' → 'dentate'
- 'toothed' → 'toothed'
- 'undulate' → 'undulate'
- 'ciliate' → 'ciliate'
- 'lobed' → 'lobed'
- 'serrate, ciliate' → 'serrate, ciliate'
- 'elliptic' → '' (this is leaf shape, not margin)
- 'ovate' → '' (this is leaf shape, not margin)
- 'deciduous' → '' (this is leaf duration, not margin)
- 'alternate' → '' (this is leaf arrangement, not margin)
- 'smooth' → '' (this is leaf texture, not margin)

If no leaf margin information is stated, return an empty string.

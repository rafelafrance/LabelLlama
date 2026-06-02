`plantSizes` (list[str]): Extract dimensions of individual plant parts and structures, excluding the overall plant height (which belongs in `plantHeight`). This is a catch-all for measurements of specific organs, tissues, or features. Each entry should be a self-contained measurement with units. It is distinct from `plantHeight` (total vertical size of the whole plant), which has its own field.

✅ Include:
- Leaf dimensions: 'leaves 5-10 cm long', 'leaf blade 3 cm wide', 'petiole 2 cm', 'stipules 1 mm'
- Flower dimensions: 'corolla 1.5 cm wide', 'petals 8 mm long', 'sepals 4 mm', 'stamens 6 mm', 'style 1 cm', 'ovary 2 mm'
- Fruit/seed dimensions: 'fruit 3 mm diam', 'capsule 5 cm long', 'nut 1 cm wide', 'seed 2 mm', 'berry 8 mm diam'
- Stem/trunk dimensions: 'stem 2 cm thick', 'trunk 30 cm diam', 'cane 1 cm wide', 'branch 5 mm thick', 'rhizome 2 cm diam'
- Underground structures: 'bulb 5 cm wide', 'corm 3 cm diam', 'tuber 4 cm long', 'rootstock 10 cm'
- Growth/architectural dimensions: 'crown 2 m wide', 'spread 1.5 m', 'internodes 3 cm', 'branches 20 cm long'
- Compound measurements: 'leaves 5-10 cm × 2-4 cm', 'corolla 1.5 cm diam, lobes 8 mm'

❌ DO NOT include:
- Overall plant height — those belong in `plantHeight` (e.g., '1.5 m tall', 'up to 3 m', '10 cm high')
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate', 'creeping')
- Woodiness — those belong in `woodiness` (e.g., 'woody', 'herbaceous')
- Life cycle — those belong in `lifeCycle` (e.g., 'annual', 'perennial')
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous')
- Developmental or phenological stage — those belong in `lifeStage` (e.g., 'seedling', 'flowering', 'dormant')
- Ecological life form — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic')
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Labels or prefixes (e.g., 'size:', 'dimensions:', 'meas.') — extract only the measurement itself

Note: When a label contains both overall height and part sizes (e.g., '1 m tall, leaves 5 cm, flowers 1 cm wide'), extract only the part sizes into this field ('leaves 5 cm', 'flowers 1 cm wide') and leave the overall height for `plantHeight`. Each measurement should be a separate list entry. If a single phrase contains multiple part sizes, split them into individual entries when they describe different organs.

Normalization: Preserve the text exactly as written, including units, ranges, and any qualifiers. Do not convert units (e.g., keep '3 ft wide' as '3 ft wide', do not change to '0.9 m wide'). Do not standardize abbreviations (e.g., keep 'diam.', 'long', 'wide' as written).

Examples:
- 'leaves 5-10 cm long' → ['leaves 5-10 cm long']
- 'corolla 1.5 cm wide' → ['corolla 1.5 cm wide']
- 'fruit 3 mm diam' → ['fruit 3 mm diam']
- 'stem 2 cm thick' → ['stem 2 cm thick']
- 'bulb 5 cm wide' → ['bulb 5 cm wide']
- 'leaves 5-10 cm × 2-4 cm' → ['leaves 5-10 cm × 2-4 cm']
- 'leaves 5 cm, flowers 1 cm wide, fruit 3 mm' → ['leaves 5 cm', 'flowers 1 cm wide', 'fruit 3 mm']
- '1.5 m tall' → [] (this is overall height, not part size)
- 'up to 3 m' → [] (this is overall height, not part size)
- 'erect' → [] (this is habit, not size)
- 'woody' → [] (this is woodiness, not size)
- 'in forest' → [] (this is habitat, not size)
- 'common' → [] (this is abundance, not size)

If no size information for individual plant parts is stated, return an empty list.

`woodiness` (str): Extract the degree of woodiness of the plant (whether the stem is woody or herbaceous). This describes the nature of the above-ground tissue at the end of the growing season — specifically, whether the stem persists as hard, lignified tissue or dies back as soft, green tissue. It is distinct from `habit` (growth shape/orientation, e.g., 'erect', 'climbing'), `lifeForm` (nutritional strategy or substrate, e.g., 'epiphytic', 'parasitic'), and `lifeCycle` (plant lifespan, e.g., 'annual', 'perennial').

✅ Include:
- Fully woody: 'woody', 'tree', 'arborescent', 'shrub', 'frutescent', 'fruticose', 'shrublet', 'subshrub', 'suffrutescent', 'suffruticose', 'lignified', 'lignified at base', 'woody caudex', 'woody rootstock'
- Partially woody: 'semi-woody', 'partly woody', 'woody-based', 'woody stem', 'base woody', 'lower stem woody', 'subshrub-like', 'semi-suffrutescent'
- Herbaceous: 'herbaceous', 'herb', 'subherbaceous', 'soft-stemmed', 'succulent', 'fleshy', 'juicy', 'watery'
- Compound descriptors: 'herbaceous perennial', 'herbaceous annual', 'woody perennial', 'woody annual', 'succulent herb'

❌ DO NOT include:
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate', 'creeping', 'vine')
- Ecological life form — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic', 'aquatic', 'lithophytic')
- Life cycle or duration — those belong in `lifeCycle` (e.g., 'annual', 'biennial', 'perennial', 'short-lived')
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous', 'semi-evergreen')
- Developmental or phenological stage — those belong in `lifeStage` (e.g., 'seedling', 'flowering', 'dormant')
- Breeding system — those belong in `reproduction` (e.g., 'dioecious', 'monoecious')
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow', 'rocky slope')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Labels or prefixes (e.g., 'woodiness:', 'stem type:') — extract only the woodiness term itself

Note: 'herbaceous perennial' and 'woody perennial' contain both woodiness and life cycle information. Extract the full compound phrase into `woodiness` (e.g., 'herbaceous perennial') and also extract 'perennial' into `lifeCycle`. When only 'herbaceous' or 'woody' appears without a life cycle qualifier, extract it solely into `woodiness`. Terms like 'succulent' describe water-storage tissue and belong in `woodiness` as a subtype of herbaceous tissue, not in `lifeForm`.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'suffrutescent' or 'suffruticose' as written). If multiple woodiness terms are listed, keep them as they appear.

Examples:
- 'woody' → 'woody'
- 'herbaceous' → 'herbaceous'
- 'subshrub' → 'subshrub'
- 'suffrutescent' → 'suffrutescent'
- 'semi-woody' → 'semi-woody'
- 'lignified' → 'lignified'
- 'succulent' → 'succulent'
- 'fleshy' → 'fleshy'
- 'herbaceous perennial' → 'herbaceous perennial'
- 'woody-based' → 'woody-based'
- 'lignified at base' → 'lignified at base'
- 'erect' → '' (this is habit, not woodiness)
- 'climbing' → '' (this is habit, not woodiness)
- 'prostrate' → '' (this is habit, not woodiness)
- 'epiphytic' → '' (this is life form, not woodiness)
- 'parasitic' → '' (this is life form, not woodiness)
- 'annual' → '' (this is life cycle, not woodiness)
- 'perennial' → '' (this is life cycle, not woodiness)
- 'deciduous' → '' (this is leaf duration, not woodiness)
- 'flowering' → '' (this is life stage, not woodiness)
- 'dioecious' → '' (this is breeding system, not woodiness)
- 'in forest' → '' (this is habitat, not woodiness)
- 'common' → '' (this is abundance, not woodiness)

If no woodiness information is stated, return an empty string.

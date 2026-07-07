---
name: lifeForm
description: Extract the ecological life form (aka niche) of the specimen
module: llama/fields/plants/lifeForm.py
---

# Prompt lifeForm

`lifeForm` (str): Extract the ecological life form (aka niche) of the specimen. This describes how the plant obtains nutrients, how it anchors itself to its substrate, and its physiological adaptation to environmental conditions. It is distinct from habit (growth shape/orientation, e.g., 'erect', 'climbing'), habitat (physical environment/location, e.g., 'forest', 'meadow', 'desert'), woodiness (stem tissue nature, e.g., 'woody', 'herbaceous'), and life cycle (plant lifespan, e.g., 'annual', 'perennial').

✅ Include:
- Nutritional strategy: 'parasitic', 'hemiparasitic', 'holoparasitic', 'saprophytic', 'saprotrophic', 'mycoheterotrophic', 'myco-heterotrophic', 'heterotrophic', 'chlorophyllous', 'achlorophyllous', 'autotrophic', 'carnivorous', 'insectivorous'
- Substrate association (where/how the plant anchors): 'epiphyte', 'epiphytic', 'lithophyte', 'lithophytic', 'saxicolous', 'saxatile', 'terrestrial', 'geophyte', 'geophytic', 'rhizomatous', 'bulbous', 'tuberous', 'caulescent', 'acaulescent'
- Environmental adaptation (physiological tolerance/adaptation, not location): 'aquatic', 'semi-aquatic', 'amphibious', 'hydrophytic', 'halophyte', 'halophytic', 'littoral', 'riparian', 'xerophytic', 'hygrophytic', 'helophytic'
- Symbiotic/associative: 'mycorrhizal', 'nitrogen-fixing', 'lichened'

❌ DO NOT include:
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate', 'creeping', 'vine')
- Physical habitat/location — those belong in `habitat` (e.g., 'forest', 'meadow', 'desert', 'rocky slope', 'stream bank', 'along roadsides')
- Woodiness (stem tissue nature) — those belong in `woodiness` (e.g., 'woody', 'herbaceous', 'succulent', 'lignified')
- Life cycle or duration — those belong in `lifeCycle` (e.g., 'annual', 'biennial', 'perennial')
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous')
- Developmental or phenological stage — those belong in `lifeStage` (e.g., 'seedling', 'flowering', 'dormant')
- Breeding system — those belong in `reproduction` (e.g., 'dioecious', 'monoecious')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Labels or prefixes (e.g., 'life form:', 'ecology:') — extract only the life form term itself

Note: Terms like 'aquatic', 'riparian', 'littoral', 'xerophytic', and 'halophytic' can blur the line between life form and habitat. Use context to decide: if the term describes the plant's physiological adaptation or ecological classification (e.g., 'a xerophytic species', 'halophytic'), it belongs in `lifeForm`. If it describes the collection site or location (e.g., 'in aquatic habitat', 'along riparian zone'), it belongs in `habitat`. Similarly, 'terrestrial' is a life form when contrasting with 'epiphytic' or 'aquatic', but is too generic to extract if it's the only descriptor and clearly just states the obvious ground-dwelling nature.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'mycoheterotrophic' or 'myco-heterotrophic' as written). If multiple life form terms are listed, keep them as they appear.

Examples:
- 'epiphytic' → 'epiphytic'
- 'parasitic' → 'parasitic'
- 'hemiparasitic' → 'hemiparasitic'
- 'aquatic' → 'aquatic'
- 'lithophytic' → 'lithophytic'
- 'xerophytic' → 'xerophytic'
- 'halophytic' → 'halophytic'
- 'mycoheterotrophic' → 'mycoheterotrophic'
- 'carnivorous' → 'carnivorous'
- 'bulbous' → 'bulbous'
- 'rhizomatous' → 'rhizomatous'
- 'achlorophyllous' → 'achlorophyllous'
- 'erect' → '' (this is habit, not life form)
- 'climbing' → '' (this is habit, not life form)
- 'in forest' → '' (this is habitat, not life form)
- 'woody' → '' (this is woodiness, not life form)
- 'herbaceous' → '' (this is woodiness, not life form)
- 'annual' → '' (this is life cycle, not life form)
- 'deciduous' → '' (this is leaf duration, not life form)
- 'flowering' → '' (this is life stage, not life form)
- 'dioecious' → '' (this is breeding system, not life form)
- 'common' → '' (this is abundance, not life form)

If no life form information is stated, return an empty string.

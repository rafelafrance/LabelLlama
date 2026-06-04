---
name: lifeStage
description: Extract the developmental or phenological stage of the specimen
module: llama/fields/plants/lifeStage.py
---

# Prompt lifeStage

`lifeStage` (str): Extract the developmental or phenological stage of the specimen. This describes the current growth phase, maturity level, or reproductive state of the plant at the time of collection. It is distinct from life cycle (plant lifespan, e.g., 'annual', 'perennial'), flowersPresent/fruitPresent (boolean indicators of reproductive parts), and leaf duration (how long leaves are retained, e.g., 'evergreen', 'deciduous').

✅ Include:
- Developmental maturity: 'seedling', 'juvenile', 'immature', 'young', 'mature', 'adult', 'old', 'senescent', 'established', 'sapling', 'seed', 'propagule', 'tissue culture', 'ex vitro', 'cultivated', 'naturalized', 'wild'
- Reproductive/phenological state: 'flowering', 'in flower', 'blooming', 'fruiting', 'in fruit', 'seeding', 'in seed', 'flower and fruit', 'fl. and fr.', 'flowering and fruiting', 'flowering and seeding', 'in bloom', 'anthesis'
- Seasonal/resting state: 'dormant', 'dormancy', 'resting', 'dormant with buds', 'dormant with flower buds', 'dormant with fruit', 'leafless', 'bare'
- Vegetative state: 'vegetative', 'leafy', 'in leaf', 'leafing out', 'new growth', 'flushing'
- Post-reproductive/decline: 'senescing', 'declining', 'withered', 'dried', 'dead', 'dead wood'

❌ DO NOT include:
- Life cycle or duration — those belong in `lifeCycle` (e.g., 'annual', 'biennial', 'perennial', 'short-lived', 'long-lived')
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous', 'semi-evergreen', 'marcescent')
- Woodiness (stem tissue nature) — those belong in `woodiness` (e.g., 'woody', 'herbaceous', 'succulent')
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate')
- Ecological life form — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic', 'aquatic')
- Breeding system — those belong in `reproduction` (e.g., 'dioecious', 'monoecious')
- Flower or fruit sex — those belong in `sex` (e.g., 'male', 'female', 'bisexual')
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow', 'rocky slope')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Labels or prefixes (e.g., 'stage:', 'phenology:') — extract only the life stage term itself

Note: 'flowering' and 'fruiting' describe the current phenological state and belong in `lifeStage`, while `flowersPresent` and `fruitPresent` are separate boolean fields. Both should be populated when relevant — `lifeStage` captures the descriptive text, while the booleans capture the presence/absence signal. Similarly, 'dormant with flower buds' implies both dormancy (life stage) and potential flowering (may inform `flowersPresent` depending on context).

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'fl. and fr.' or 'flowering and fruiting' as written). If multiple life stage terms are listed, keep them as they appear.

Examples:
- 'flowering' → 'flowering'
- 'in flower' → 'in flower'
- 'fruiting' → 'fruiting'
- 'in fruit' → 'in fruit'
- 'flower and fruit' → 'flower and fruit'
- 'fl. and fr.' → 'fl. and fr.'
- 'seedling' → 'seedling'
- 'mature' → 'mature'
- 'dormant' → 'dormant'
- 'dormant with flower buds' → 'dormant with flower buds'
- 'vegetative' → 'vegetative'
- 'senescent' → 'senescent'
- 'in leaf' → 'in leaf'
- 'annual' → '' (this is life cycle, not life stage)
- 'perennial' → '' (this is life cycle, not life stage)
- 'evergreen' → '' (this is leaf duration, not life stage)
- 'deciduous' → '' (this is leaf duration, not life stage)
- 'woody' → '' (this is woodiness, not life stage)
- 'erect' → '' (this is habit, not life stage)
- 'epiphytic' → '' (this is life form, not life stage)
- 'dioecious' → '' (this is breeding system, not life stage)
- 'male' → '' (this is flower sex, not life stage)
- 'in forest' → '' (this is habitat, not life stage)
- 'common' → '' (this is abundance, not life stage)

If no life stage information is stated, return an empty string.

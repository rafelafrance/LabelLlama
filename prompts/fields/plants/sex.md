`sex` (str): Extract the sex of the individual flower(s) or inflorescence on the specimen. This describes whether the flowers on this particular specimen contain male reproductive parts only, female reproductive parts only, both, or neither. It is distinct from `reproduction` (breeding system at the population/species level, e.g., 'dioecious', 'monoecious') and from `lifeStage` (phenological state, e.g., 'flowering', 'fruiting').

✅ Include:
- Basic flower sex: 'male', 'female', 'bisexual', 'perfect', 'imperfect', 'unisexual'
- Male-only terms: 'staminate', 'staminate flowers', 'staminal', 'staminode'
- Female-only terms: 'pistillate', 'pistillate flowers', 'pistillode'
- Structural arrangements: 'monoclinous', 'diclinous', 'synoecious', 'dioicous'
- Non-functional/sterile: 'neuter', 'neutral', 'sterile', 'sterile flowers'
- Opening/mating behavior: 'cleistogamous', 'chasmogamous'
- Mixed/ambiguous sex: 'androgynous', 'hermaphroditic' (when describing individual flowers, not the population)

❌ DO NOT include:
- Breeding system (population-level) — those belong in `reproduction` (e.g., 'dioecious', 'monoecious', 'polygamous', 'gynodioecious', 'androdioecious')
- Phenological or developmental stage — those belong in `lifeStage` (e.g., 'flowering', 'fruiting', 'in bloom', 'dormant')
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate')
- Woodiness — those belong in `woodiness` (e.g., 'woody', 'herbaceous')
- Life cycle — those belong in `lifeCycle` (e.g., 'annual', 'perennial')
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous')
- Ecological life form — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic')
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Pollination syndrome or agents — those belong in their respective fields (e.g., 'wind-pollinated', 'entomophilous')
- Labels or prefixes (e.g., 'sex:', 'flower sex:', '♂', '♀') — extract only the sex term itself

Note: 'androgynous' and 'hermaphroditic' can describe either individual flower sex (belonging in `sex`) or a population-level breeding system (belonging in `reproduction`). Use context to decide: if describing the specimen's own flowers, it belongs in `sex`. If describing the species' reproductive strategy alongside terms like 'monoecious'/'dioecious', it belongs in `reproduction`. When both flower sex and breeding system appear on the same label, extract each into its respective field.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'staminate' or 'staminate flowers' as written). If multiple sex terms are listed, keep them as they appear.

Examples:
- 'male' → 'male'
- 'female' → 'female'
- 'bisexual' → 'bisexual'
- 'perfect' → 'perfect'
- 'imperfect' → 'imperfect'
- 'staminate' → 'staminate'
- 'pistillate' → 'pistillate'
- 'unisexual' → 'unisexual'
- 'neuter' → 'neuter'
- 'cleistogamous' → 'cleistogamous'
- 'chasmogamous' → 'chasmogamous'
- 'diclinous' → 'diclinous'
- 'dioecious' → '' (this is breeding system, not flower sex)
- 'monoecious' → '' (this is breeding system, not flower sex)
- 'polygamous' → '' (this is breeding system, not flower sex)
- 'flowering' → '' (this is life stage, not flower sex)
- 'fruiting' → '' (this is life stage, not flower sex)
- 'erect' → '' (this is habit, not flower sex)
- 'woody' → '' (this is woodiness, not flower sex)
- 'annual' → '' (this is life cycle, not flower sex)
- 'evergreen' → '' (this is leaf duration, not flower sex)
- 'epiphytic' → '' (this is life form, not flower sex)
- 'in forest' → '' (this is habitat, not flower sex)
- 'common' → '' (this is abundance, not flower sex)
- 'wind-pollinated' → '' (this is pollination, not flower sex)

If no flower sex information is stated, return an empty string.

---
name: reproduction
description: Extract the plant's breeding system (how sexual organs are distributed among flowers and individuals across the population)
---

# Prompt reproduction

`reproduction` (str): Extract the plant's breeding system (how sexual organs are distributed among flowers and individuals across the population). This describes whether male and female reproductive parts occur together or separately at the species/population level. It is distinct from `sex` (which describes the sex of individual flowers on the specimen, e.g., 'male', 'female', 'bisexual') and from `lifeStage` (which describes the phenological state, e.g., 'flowering', 'fruiting').

✅ Include:
- Basic breeding systems: 'monoecious', 'dioecious', 'polygamous', 'polygamomonoecious', 'polygamodioecious', 'gynodioecious', 'gynodioecy', 'androdioecious', 'trioecious', 'trimonoecious'
- Variant/intermediate systems: 'subdioecious', 'subandroecious', 'subgynoecious', 'andromonoecious', 'gynomonoecious', 'androecious', 'gynoecious'
- Combined/complex systems: 'androgynous', 'androgynomonoecious', 'hermaphroditic', 'hermaphrodite'
- Temporal separation of sex expression: 'dichogamous', 'protandrous', 'protogynous'
- Asexual/clonal reproduction: 'vegetative reproduction', 'apomictic', 'apomixis', 'clonal', 'rhizomatous reproduction', 'stoloning'

❌ DO NOT include:
- Individual flower sex — those belong in `sex` (e.g., 'male', 'female', 'bisexual', 'staminate', 'pistillate', 'unisexual', 'perfect', 'imperfect')
- Phenological or developmental stage — those belong in `lifeStage` (e.g., 'flowering', 'fruiting', 'in bloom', 'dormant')
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate')
- Woodiness — those belong in `woodiness` (e.g., 'woody', 'herbaceous')
- Life cycle — those belong in `lifeCycle` (e.g., 'annual', 'perennial')
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous')
- Ecological life form — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic')
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Pollination syndrome or agents — those belong in their respective fields (e.g., 'wind-pollinated', 'insect-pollinated', 'entomophilous')
- Labels or prefixes (e.g., 'breeding system:', 'sex system:') — extract only the term itself

Note: 'androgynous' can describe either individual flower sex (belonging in `sex`) or a population-level breeding system (belonging in `reproduction`). Use context to decide: if paired with 'monoecious'/'dioecious' or describing the species' reproductive strategy, it belongs in `reproduction`. If describing a single flower's structure, it belongs in `sex`. 'rhizomatous' can describe either clonal reproduction (belonging in `reproduction`) or substrate association (belonging in `lifeForm`). Use context to decide.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'gynodioecy' or 'gynodioecious' as written). If multiple breeding system terms are listed, keep them as they appear.

Examples:
- 'monoecious' → 'monoecious'
- 'dioecious' → 'dioecious'
- 'polygamous' → 'polygamous'
- 'gynodioecious' → 'gynodioecious'
- 'androdioecious' → 'androdioecious'
- 'protandrous' → 'protandrous'
- 'protogynous' → 'protogynous'
- 'hermaphroditic' → 'hermaphroditic'
- 'apomictic' → 'apomictic'
- 'dichogamous' → 'dichogamous'
- 'male' → '' (this is flower sex, not breeding system)
- 'female' → '' (this is flower sex, not breeding system)
- 'bisexual' → '' (this is flower sex, not breeding system)
- 'staminate' → '' (this is flower sex, not breeding system)
- 'flowering' → '' (this is life stage, not breeding system)
- 'fruiting' → '' (this is life stage, not breeding system)
- 'erect' → '' (this is habit, not breeding system)
- 'woody' → '' (this is woodiness, not breeding system)
- 'annual' → '' (this is life cycle, not breeding system)
- 'evergreen' → '' (this is leaf duration, not breeding system)
- 'epiphytic' → '' (this is life form, not breeding system)
- 'in forest' → '' (this is habitat, not breeding system)
- 'common' → '' (this is abundance, not breeding system)
- 'wind-pollinated' → '' (this is pollination, not breeding system)

If no breeding system information is stated, return an empty string.

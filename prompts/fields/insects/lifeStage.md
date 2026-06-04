---
name: lifeStage
description: Extract the developmental or phenological stage of the insect specimen at the time of collection. This describes the life cycle phase or maturity level of the organism
---

# Prompt

`lifeStage` (str): Extract the developmental or phenological stage of the insect specimen at the time of collection. This describes the life cycle phase or maturity level of the organism.

✅ Include:
- Holometabolous stages: 'egg', 'larva', 'pupa', 'adult', 'imago'
- Hemimetabolous stages: 'egg', 'nymph', 'adult', 'imago'
- Common stage synonyms: 'caterpillar', 'maggot', 'grub', 'naiad', 'chrysalis', 'cocoon'
- Sub-stage indicators: '1st instar', 'final instar', 'prepupa', 'pharate adult', 'teneral'
- Wandering or transitional stages: 'wandering larva', 'wandering stage'
- Mass rearing or batch descriptors when implying stage: 'eggs (batch)', 'larval colony'

❌ DO NOT include:
- Sex designations: 'male', 'female', '♂', '♀' (those belong in `sex`)
- Social-insect castes: 'queen', 'worker', 'soldier', 'drone' (those describe morphology, not development)
- Reproductive status: 'gravid', 'mated', 'ovipositing'
- Condition or preservation state: 'damaged', 'fragment', 'slide mount', 'alcohol'
- Phenological notes unrelated to development: 'in flower', 'in fruit', 'emergent'

Normalization: Return the value exactly as written on the label — do not translate common names to technical terms (e.g., keep 'caterpillar', do not change to 'larva'). If no life stage information is stated, return an empty string.

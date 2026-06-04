---
name: leafDuration
description: Extract the leaf duration (how long the plant retains its leaves through the growing season and/or winter). This describes whether the plant sheds its leaves seasonally or keeps them year-round
---

# Prompt

`leafDuration` (str): Extract the leaf duration (how long the plant retains its leaves through the growing season and/or winter). This describes whether the plant sheds its leaves seasonally or keeps them year-round.

✅ Include:
- Full retention: 'evergreen', 'perennial' (when referring to leaf retention, not life cycle)
- Seasonal shedding: 'deciduous', 'caducous', 'abscissile'
- Partial/intermediate retention: 'semi-deciduous', 'semi-evergreen', 'partly evergreen', 'sub-evergreen'
- Retention beyond normal season: 'marcescent', 'persistent', 'retaining leaves', 'holding leaves'
- Early/late leafing: 'pre-vernal', 'vernal', 'late-leafing', 'early-deciduous'

❌ DO NOT include:
- Life cycle or plant lifespan — those belong in `lifeCycle` (e.g., 'annual', 'biennial', 'perennial' as plant duration)
- Leaf shape or margin — those belong in `leafShape` and `leafMargin`
- Leaf color or texture — those belong in their respective fields
- Phenology or developmental stage — those belong in `lifeStage` (e.g., 'in leaf', 'leafing out')
- Habitat or environmental descriptors — those belong in `habitat`
- Labels or prefixes (e.g., 'leaf duration:', 'foliage:') — extract only the duration term itself

Note: 'marcescent' and 'persistent' can appear in both leaf duration and life cycle contexts. In leaf duration, they describe leaves retained beyond their normal abscission time. In life cycle, they describe the plant's overall longevity. Use context to determine the correct field.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms. If multiple leaf duration terms are listed, keep them as they appear.

Examples:
- 'deciduous' → 'deciduous'
- 'evergreen' → 'evergreen'
- 'semi-deciduous' → 'semi-deciduous'
- 'semi-evergreen' → 'semi-evergreen'
- 'marcescent' → 'marcescent'
- 'persistent' → 'persistent'
- 'retaining leaves' → 'retaining leaves'
- 'annual' → '' (this is life cycle, not leaf duration)
- 'biennial' → '' (this is life cycle, not leaf duration)
- 'elliptic' → '' (this is leaf shape, not leaf duration)
- 'in leaf' → '' (this is phenology, not leaf duration)

If no leaf duration information is stated, return an empty string.

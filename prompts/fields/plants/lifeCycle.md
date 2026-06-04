---
name: lifeCycle
description: Extract the plant's life cycle or duration (how long the plant lives over the course of its lifetime)
---

# Prompt

`lifeCycle` (str): Extract the plant's life cycle or duration (how long the plant lives over the course of its lifetime). This describes the number of growing seasons required to complete the life cycle and the plant's reproductive strategy. It is distinct from leaf duration (how long leaves are retained, e.g., 'evergreen', 'deciduous'), life stage (current developmental phase, e.g., 'seedling', 'flowering'), and woodiness (stem tissue nature, e.g., 'woody', 'herbaceous').

✅ Include:
- Standard life cycle terms: 'annual', 'biennial', 'perennial', 'short-lived perennial', 'short-lived', 'long-lived', 'long-lived perennial'
- Reproductive strategy terms: 'monocarpic', 'semelparous', 'iteroparous', 'polycarpic'
- Transient/ephemeral terms: 'fugacious', 'ephemeral', 'short-lived', 'transient'
- Persistence/retention terms (when describing overall plant longevity, not leaves): 'persistent', 'subpersistent', 'perennial' (when clearly referring to life cycle, not leaf retention)
- Duration descriptors: 'one-year', 'two-year', 'multi-year', 'several years', 'decades', 'centuries'

❌ DO NOT include:
- Leaf duration — those belong in `leafDuration` (e.g., 'evergreen', 'deciduous', 'semi-evergreen')
- Developmental or phenological stage — those belong in `lifeStage` (e.g., 'seedling', 'flowering', 'fruiting', 'dormant', 'mature')
- Woodiness (stem tissue nature) — those belong in `woodiness` (e.g., 'woody', 'herbaceous', 'succulent')
- Growth habit or shape — those belong in `habit` (e.g., 'erect', 'climbing', 'prostrate')
- Ecological life form — those belong in `lifeForm` (e.g., 'epiphytic', 'parasitic', 'aquatic')
- Habitat or physical environment — those belong in `habitat` (e.g., 'forest', 'meadow', 'rocky slope')
- Abundance or frequency — those belong in `abundance` (e.g., 'common', 'rare')
- Labels or prefixes (e.g., 'life cycle:', 'duration:') — extract only the life cycle term itself

Note: 'perennial' can refer to either life cycle (plant lives multiple years) or leaf duration (leaves persist year-round). Use context to decide: if paired with 'evergreen'/'deciduous' or describing foliage, it belongs in `leafDuration`. If standing alone or describing the plant's overall lifespan, it belongs in `lifeCycle`. 'marcescent' and 'persistent' can also appear in both contexts — in life cycle they describe the plant's overall longevity, in leaf duration they describe leaves retained beyond their normal abscission time.

Normalization: Return the term exactly as written on the label. Do not standardize synonyms (e.g., keep 'short-lived perennial' as written, do not simplify to 'perennial'). If multiple life cycle terms are listed, keep them as they appear.

Examples:
- 'annual' → 'annual'
- 'biennial' → 'biennial'
- 'perennial' → 'perennial'
- 'short-lived perennial' → 'short-lived perennial'
- 'long-lived' → 'long-lived'
- 'fugacious' → 'fugacious'
- 'monocarpic' → 'monocarpic'
- 'iteroparous' → 'iteroparous'
- 'persistent' → 'persistent'
- 'deciduous' → '' (this is leaf duration, not life cycle)
- 'evergreen' → '' (this is leaf duration, not life cycle)
- 'herbaceous' → '' (this is woodiness, not life cycle)
- 'woody' → '' (this is woodiness, not life cycle)
- 'flowering' → '' (this is life stage, not life cycle)
- 'seedling' → '' (this is life stage, not life cycle)
- 'erect' → '' (this is habit, not life cycle)
- 'epiphytic' → '' (this is life form, not life cycle)

If no life cycle information is stated, return an empty string.

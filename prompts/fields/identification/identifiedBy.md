---
name: identifiedBy
description: Extract the name of the person or group who identified, determined, or verified the taxonomic name of the specimen. This is the determiner, not the original collector
---

# Prompt

`identifiedBy` (str): Extract the name of the person or group who identified, determined, or verified the taxonomic name of the specimen. This is the determiner, not the original collector.

✅ Include:
- Individual determiners: 'J. Doe', 'A. B. Smith', 'Maria Garcia'
- Multiple determiners: 'Smith & Jones', 'A. B. & C. D.'
- Institutional identifiers: 'USDA Taxonomy Lab', 'CalFlora ID Team'
- Names appearing with labels like 'det.', 'det. by', 'id.', 'id. by', 'identified by', 'verified by', 'conf.' — extract only the name
- Re-identifiers or revised determiners (use the most recent or primary identifier if multiple are listed)

❌ DO NOT include:
- Determiner labels themselves ('det.', 'det. by', 'id.', 'verified by') — extract only the value
- Collector names — those belong in `recordedBy` (e.g., 'col. J. Smith' is the collector, not the identifier)
- Preparator or mounting personnel (e.g., 'prep. by', 'mounted by')
- Date of identification — that belongs in `dateIdentified`
- Database or repository names (e.g., 'GBIF', 'iNaturalist') unless they represent the actual identifying authority

Normalization: Preserve the name exactly as written — do not expand abbreviations or reorder names. If no identifier is named, return an empty string.

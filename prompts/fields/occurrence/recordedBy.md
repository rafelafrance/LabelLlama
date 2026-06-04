---
name: recordedBy
description: Extract the name of the person or group who collected or observed the specimen. This is the primary collector, not the person who later identified or cataloged it
---

# Prompt

`recordedBy` (str): Extract the name of the person or group who collected or observed the specimen. This is the primary collector, not the person who later identified or cataloged it.

✅ Include:
- Individual collector names: 'J. Smith', 'A. B. Anderson', 'Maria Garcia'
- Multiple collectors: 'Smith & Jones', 'A. B. & C. D.', 'Smith, Jones, and Lee'
- Institutional or team collectors: 'USDA Plant Introduction Team', 'CalFlora Survey 2010'
- Collector names with associated numbers if they form a single compound identifier (e.g., 'Smith 1234')
- Names appearing with labels like 'col.', 'coll.', 'coll. by', 'collected by' — extract only the name

❌ DO NOT include:
- Collector labels themselves ('col.', 'coll.', 'collected by') — extract only the value
- Determiner or identifier names — those belong in `identifiedBy` (e.g., 'det. by J. Doe', 'id. by', 'verified by')
- Preparator or mounting personnel (e.g., 'prep. by', 'mounted by')
- Record numbers or collector accession numbers — those belong in `recordNumber`
- Database or repository names (e.g., 'GBIF', 'iNaturalist') unless they represent the actual collecting team

Normalization: Preserve the name exactly as written — do not expand abbreviations or reorder names. If no collector is named, return an empty string.

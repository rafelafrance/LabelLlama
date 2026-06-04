---
name: recordNumber
description: Extract the record number — an identifier assigned to the occurrence at the time it was recorded. This often serves as a link between field notes and the occurrence record, such as a collector's field number or accession number
---

# Prompt

`recordNumber` (str): Extract the record number — an identifier assigned to the occurrence at the time it was recorded. This often serves as a link between field notes and the occurrence record, such as a collector's field number or accession number.

✅ Include:
- Collector field numbers: '12345', 'S-4567', '2010-001'
- Collector number compounds: 'Smith 1234', 'Anderson 456', 'Garcia & Lee 789'
- Accession numbers: 'acc. 4567', 'accession 123'
- Numbers preceded by '#' or 'Nº': '#5678', 'Nº 123'
- Field trip or expedition codes used as occurrence identifiers: 'Expedition 2015-A', 'Trip 42'

❌ DO NOT include:
- Catalog numbers assigned by the institution — those belong in `catalogNumber` (e.g., 'ALMNH:Ento:137097', 'USNM 123456')
- Collector names alone — those belong in `recordedBy`
- Database-generated IDs (e.g., UUIDs, GBIF occurrence keys, iNaturalist observation IDs)
- License or permit numbers (e.g., 'Permit #123', 'Collection Permit 2020-05')
- Labels themselves ('rec. no.', 'record number', 'field no.') — extract only the value

Normalization: Preserve the value exactly as written — do not strip prefixes, expand abbreviations, or reformat. If no record number is present, return an empty string.

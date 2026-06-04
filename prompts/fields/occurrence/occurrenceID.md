---
name: occurrenceID
description: Extract the occurrence ID — a unique identifier for the physical specimen or observation (as opposed to a particular digital record of it)
---

# occurrenceID

`occurrenceID` (str): Extract the occurrence ID — a unique identifier for the physical specimen or observation (as opposed to a particular digital record of it).

✅ Include:
- Unique identifiers for the physical specimen or observation: 'OCC-12345', 'SPEC-67890', 'USNM:ENT:123456'
- Dataset or repository occurrence keys: 'GBIF:12345678', 'iNaturalist:987654321'
- Persistent URIs or URNs: 'http://arctos.database.museum/guid/MSB:Mamm:233627', 'urn:catalog:UWBM:Bird:89776'
- UUIDs: '000866d2-c177-4648-a200-ead4007051b9'
- IDs preceded by '#' or 'Nº': '#5678', 'Nº 123'

❌ DO NOT include:
- Catalog numbers assigned by the institution — those belong in `catalogNumber` (unless they serve as the primary occurrence ID)
- Record numbers or collector field numbers — those belong in `recordNumber`
- Database-generated record IDs that are not tied to the physical occurrence
- Labels themselves ('occurrence ID:', 'ID:', 'identifier') — extract only the value

Normalization: Preserve the identifier exactly as written — do not truncate, reformat, or resolve URLs. If no occurrence ID is present, return an empty string.

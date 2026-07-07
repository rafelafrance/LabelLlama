---
name: identifiedByID
description: Extract the globally unique identifier for the person, group, or organization responsible for assigning the taxon to the specimen. This is a machine-readable ID, not a human-readable name
module: llama/fields/identification/identifiedByID.py
---

# Prompt identifiedByID

`identifiedByID` (str): Extract the globally unique identifier for the person, group, or organization responsible for assigning the taxon to the specimen. This is a machine-readable ID, not a human-readable name.

✅ Include:
- ORCID identifiers: 'https://orcid.org/0000-0002-1234-5678', '0000-0002-1234-5678'
- Institutional staff IDs: 'USNM:Staff:12345', 'CAS-ID-6789'
- Persistent URIs or URLs: 'https://www.gbif.org/scientific-authority/123456'
- LSID (Life Science Identifier): 'urn:lsid:ipni.org:names:12345-1'
- DOIs: 'https://doi.org/10.5281/zenodo.12345'
- Any other globally unique identifier associated with the determiner

❌ DO NOT include:
- Human-readable names (e.g., 'J. Doe', 'Smith & Jones') — those belong in `identifiedBy`
- Collector identifiers — those belong in `recordedBy` or related fields
- Specimen or occurrence IDs — those belong in `occurrenceID` or `catalogNumber`
- Database-generated record IDs that are not tied to the identifying person
- Labels themselves ('ORCID:', 'ID:', 'identifier') — extract only the value

Normalization: Preserve the identifier exactly as written — do not truncate, reformat, or resolve URLs. If no identified-by ID is present, return an empty string.

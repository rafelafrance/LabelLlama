---
name: catalogNumber
description: Extract the catalog number — the unique identifier for the specimen or record within its collection or data set
module: llama/fields/occurrence/catalogNumber.py
---

# Prompt catalogNumber

`catalogNumber` (str): Extract the catalog number — the unique identifier for the specimen or record within its collection or data set.

✅ Include:
- Numeric identifiers: "137097", "145732", "2008.1334"
- Alphanumeric identifiers: "145732a", "R-4313", "ENT-001234"
- The third segment of a colon-separated triplet (e.g., "137097" from "ALMNH:Ento:137097")
- Identifiers prefixed with collection or institution codes when they form a single compound ID (e.g., "CAS-ENT-12345")
- Record numbers or accession numbers used as the primary collection identifier

❌ DO NOT include:
- Institution codes (those belong in `institutionCode`)
- Collection codes (those belong in `collectionCode`)
- Field numbers, lot numbers, or collector's own numbering (e.g., "Smith 1234", "Field #567") unless used as the official catalog number
- Database-generated IDs (e.g., UUIDs, GBIF occurrence keys, iNaturalist observation IDs) unless they serve as the collection's catalog number
- Multiple catalog numbers — if present, extract only the primary one

If no catalog number is present, return an empty string.

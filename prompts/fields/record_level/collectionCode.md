---
name: collectionCode
description: Extract the collection code — the name, acronym, coden, or initialism identifying the collection or data set from which the record was derived
---

# collectionCode

`collectionCode` (str): Extract the collection code — the name, acronym, coden, or initialism identifying the collection or data set from which the record was derived.

✅ Include:
- Standard collection codes/acronyms: "Ento", "Mamm", "Bot", "Orn", "VP", "Ichth", "Malacol"
- Full collection names when used as identifiers: "Mammals", "Hildebrandt", "EBIRD", "Botanical"
- The second segment of a colon-separated triplet (e.g., "Ento" from "ALMNH:Ento:137097")
- Codes that appear alongside institution codes or catalog numbers

❌ DO NOT include:
- Institution codes (those belong in `institutionCode`)
- Catalog numbers (those belong in `catalogNumber`)
- Project names, field codes, or survey identifiers that are not collection-level identifiers
- Repository or database names (e.g., "GBIF", "iNaturalist", "BOLD") unless they represent the actual collection

If no collection code is present, return an empty string.

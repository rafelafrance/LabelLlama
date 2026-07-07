---
name: institutionCode
description: Extract the institution code — the acronym, coden, or short name used by the institution that owns the specimen or data record
module: llama/fields/record_level/institutionCode.py
---

# Prompt institutionCode

`institutionCode` (str): Extract the institution code — the acronym, coden, or short name used by the institution that owns the specimen or data record. This is typically a short uppercase or mixed-case identifier, not the full institution name.

✅ Include:
- Standard institution codes/acronyms: "ALMNH", "USNM", "CAS", "NPS", "APN", "InBio", "Museum Victoria", "AMNH"
- The first segment of a colon-separated triplet (e.g., "ALMNH" from "ALMNH:Ento:137097")
- Codes that appear alongside collection codes or catalog numbers

❌ DO NOT include:
- Full institution names (e.g., "American Museum of Natural History") — extract only the code if one is present
- Collection codes (those belong in `collectionCode`)
- Catalog numbers (those belong in `catalogNumber`)
- Repository or database names (e.g., "GBIF", "iNaturalist", "BOLD") unless they are the owning institution

If the source text contains only the full institution name with no code or acronym, return an empty string. If no institution code is present, return an empty string.

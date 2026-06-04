---
name: scientificNameAuthorship
description: Extract the authorship citation for the species-level scientific name. This is the person(s) who originally described or recombined the name
---

# Prompt scientificNameAuthorship

`scientificNameAuthorship` (str): Extract the authorship citation for the species-level scientific name. This is the person(s) who originally described or recombined the name.

✅ Include:
- Single author abbreviations (e.g., 'L.', 'Linnaeus', 'Mill.', 'Banks')
- Multiple authors joined by '&' or 'et al.' (e.g., 'Smith & Jones', 'Banks & Sol. ex Gaertn.', 'Hoffmanns. & Link')
- Parenthesized authorship indicating a name recombination (e.g., '(Bartlett) Fernald', '(L.) R.Br.')
- Publication year if present (e.g., 'L. 1753', 'Smith & Jones 1842')
- All authors as they appear — do not truncate or omit any part of the citation

❌ DO NOT include:
- Infraspecific authorship (e.g., from 'Quercus alba L. var. latifolia (Michx.) Torr.' extract 'L.', not 'L. var. latifolia (Michx.) Torr.')
- Taxonomic rank indicators ('sp.', 'var.', 'subsp.', 'sect.', 'ser.')
- Genus or species names — authorship only
- Identification qualifiers ('det. by', 'id.', 'conf.')
- Synonymy notes or alternative authorship for different ranks

Normalization: Preserve the original formatting, including parentheses, 'ex', 'et al.', and '&' as written. Do not expand abbreviations or reorder authors. If no authorship is stated, return an empty string.

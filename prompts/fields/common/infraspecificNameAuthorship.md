`infraspecificNameAuthorship` (str): Extract the authorship citation for the infraspecific name (subspecies, variety, or form). This is the person(s) who originally described or recombined the infraspecific rank, separate from the species-level authorship.

✅ Include:
- Single author abbreviations (e.g., 'Michx.', 'Torr.', 'Fernald')
- Multiple authors joined by '&' or 'et al.' (e.g., 'Smith & Jones', 'Banks & Sol.')
- Parenthesized authorship indicating a name recombination (e.g., '(Michx.) Torr.', '(L.) R.Br.')
- Publication year if present (e.g., 'Torr. 1842', 'Michx. 1803')
- 'ex' notation linking original and publishing authors (e.g., 'Banks ex Gaertn.')
- All authors as they appear — do not truncate or omit any part of the citation

❌ DO NOT include:
- Species-level authorship — that belongs in `scientificNameAuthorship` (e.g., from 'Quercus alba L. var. latifolia (Michx.) Torr.' extract '(Michx.) Torr.', not 'L.')
- The infraspecific epithet itself — that belongs in `infraspecificEpithet`
- Taxonomic rank indicators ('var.', 'subsp.', 'ssp.', 'forma', 'f.')
- Genus or species names
- Identification qualifiers ('det. by', 'id.', 'conf.')
- Labels or prefixes (e.g., 'auth.', 'author:') — extract only the authorship citation

Normalization: Preserve the original formatting, including parentheses, 'ex', 'et al.', '&', and publication years as written. Do not expand abbreviations or reorder authors.

Examples:
- 'Quercus alba L. var. latifolia (Michx.) Torr.' → '(Michx.) Torr.'
- 'Salix exigua Sm. subsp. montana Fernald' → 'Fernald'
- 'Canis lupus baileyi Merriam 1902' → 'Merriam 1902'
- 'Drosophila melanogaster f. simulans Sturtevant' → 'Sturtevant'
- 'Agoseris aurantiaca var. aurantiaca var. latifolia (Nutt.) Torr. 1842' → '(Nutt.) Torr. 1842'
- 'Canis lupus L.' → '' (no infraspecific rank, no infraspecific authorship)
- 'Salix exigua Sm.' → '' (no infraspecific rank)
- 'Pinus strobus L. subsp. montana (Smith & Jones) Fernald' → '(Smith & Jones) Fernald'

If no infraspecific authorship is stated, return an empty string.

---
name: associatedTaxa
description: Extract the name(s) of other species found with or near the specimen. This field captures taxa associated with the collection but not the primary specimen itself
---

# Prompt

`associatedTaxa` (str): Extract the name(s) of other species found with or near the specimen. This field captures taxa associated with the collection but not the primary specimen itself.

✅ Include:
- Host plants (e.g., 'on Quercus alba', 'host: Salix exigua')
- Epiphyte substrates (e.g., 'on bark of Pinus ponderosa')
- Co-occurring or companion species (e.g., 'with Agoseris aurantiaca')
- Parasites, pollinators, or symbiotic partners noted on the label
- Multiple associated taxa separated by commas or 'and'

❌ DO NOT include:
- The primary specimen's own scientific name — that belongs in `scientificName`
- Habitat or environmental descriptors that are not specific taxa (e.g., 'on rocky outcrop', 'in grassland')
- Generic descriptions (e.g., 'on a tree', 'on shrub') — extract only named taxa
- Labels or prefixes (e.g., 'host:', 'on:', 'associated with:') — extract only the taxon names
- Common/vernacular names of associated taxa unless the scientific name is not available

Normalization: Preserve the taxon names as written. If multiple associated taxa are listed, include all of them, separated by '; '. Strip labels and contextual phrases, keeping only the species or genus names.

Examples:
- 'on Quercus alba' → 'Quercus alba'
- 'host: Salix exigua' → 'Salix exigua'
- 'with Agoseris aurantiaca and Eriophyllum lanatum' → 'Agoseris aurantiaca; Eriophyllum lanatum'
- 'on bark of Pinus ponderosa' → 'Pinus ponderosa'
- 'on a tree' → '' (no specific taxon named)
- 'on rocky outcrop' → '' (habitat descriptor, not a taxon)
- 'Quercus alba (host) with Cynips quercusfolii (gall wasp)' → 'Quercus alba; Cynips quercusfolii'

If no associated taxa are mentioned, return an empty string.

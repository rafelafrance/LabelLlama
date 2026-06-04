---
name: islandGroup
description: Extract the name of the island group, archipelago, or atoll group where the specimen was collected. Return the full, standard name
---

# islandGroup

`islandGroup` (str): Extract the name of the island group, archipelago, or atoll group where the specimen was collected. Return the full, standard name.

✅ Include:
- Archipelagos: 'Galápagos', 'Aleutian Islands', 'Lesser Antilles', 'Austral Islands'
- Named island groups: 'West Indies', 'Mariana Islands', 'Bismarck Archipelago', 'Society Islands'
- Atoll groups: 'Tuamotu Archipelago', 'Chagos Archipelago'
- Named clusters or chains of islands: 'Lesser Sunda Islands', 'Banda Islands', 'Windward Islands'
- Inferred from locality or coordinates: e.g., 'Santa Cruz Island' → 'Galápagos', 'Maui' → 'Hawaiian Islands'

❌ DO NOT include:
- Individual island names — those belong in `island` (e.g., 'Hawaii', 'Vancouver Island', 'Oahu')
- Country, state/province, or other administrative divisions — those belong in `country`, `stateProvince`, `county`, `municipality`
- Specific localities, landmarks, or coordinates — those belong in `locality` or coordinate fields
- General locality descriptions (e.g., 'Pacific Islands', 'Caribbean region')

Normalization: Return the full standard name. If multiple island groups are listed, include all of them. If the island group is not stated but can be reliably inferred from the locality or coordinates, return the inferred value. If no island group information is available or inference is ambiguous, return an empty string.

---
name: island
description: Extract the name(s) of the island(s) on or near which the specimen was collected. Return the full, standard name
---

# island

`island` (str): Extract the name(s) of the island(s) on or near which the specimen was collected. Return the full, standard name.

✅ Include:
- Named islands: 'Hawaii', 'Isla de la Juventud', 'Jeju', 'Vancouver Island', 'Isle of Wight'
- Atolls, cays, and islets: 'Baker Atoll', 'Cay Sal', 'Little Island'
- Peninsulas or landmasses treated as islands on the label: 'Cape Cod', 'Oahu'
- Multiple islands listed on the label: 'Maui and Molokai', 'San Juan Islands'
- Inferred from locality or coordinates: e.g., 'Honolulu' → 'Oahu', 'Galápagos: Santa Cruz' → 'Santa Cruz Island'

❌ DO NOT include:
- Island groups or archipelagos — those belong in `islandGroup` (e.g., 'Galápagos', 'West Indies', 'Austral Islands', 'Philippines')
- Country, state/province, or other administrative divisions — those belong in `country`, `stateProvince`, `county`, `municipality`
- Specific localities, landmarks, or coordinates — those belong in `locality` or coordinate fields
- General locality descriptions (e.g., 'near shore', 'coastal area')

Normalization: Return the full standard name. If multiple islands are listed, include all of them (e.g., 'Maui and Molokai'). If the island is not stated but can be reliably inferred from the locality or coordinates, return the inferred value. If no island information is available or inference is ambiguous, return an empty string.

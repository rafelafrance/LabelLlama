---
name: county
description: Extract the county, parish, or equivalent second-level administrative division where the specimen was collected. Return the full, standard name
---

# county

`county` (str): Extract the county, parish, or equivalent second-level administrative division where the specimen was collected. Return the full, standard name.

✅ Include:
- US counties: 'Marin', 'Los Angeles', 'Cook', 'King'
- Canadian regional municipalities or census divisions: 'Halton Regional Municipality', 'Cape Breton'
- Equivalent divisions in other countries: 'parish' (Louisiana), 'borough' (Alaska), 'prefecture' (Japan), 'district' (India)
- Inferred from locality or coordinates: e.g., 'San Francisco' → 'San Francisco County', 'Toronto' → 'Toronto Division'
- Historical county names if that is what is written on the label

❌ DO NOT include:
- Country or state/province names — those belong in `country` or `stateProvince`
- Municipality or city names — those belong in `municipality`
- Specific localities, landmarks, or coordinates — those belong in `locality` or coordinate fields
- Trailing labels like 'County', 'Co.', 'Parish', 'Dist.' — extract only the name

Normalization: Return the full standard name without trailing labels (e.g., 'Marin County' → 'Marin', 'Los Angeles Co.' → 'Los Angeles'). Expand abbreviations ('Co.' → full name). If multiple counties are listed, include all of them. If the county is not stated but can be reliably inferred from the locality or coordinates, return the inferred value. If no county information is available or inference is ambiguous, return an empty string.

---
name: stateProvince
description: Extract the state, province, or equivalent first-level administrative division where the specimen was collected
module: llama/fields/location/stateProvince.py
---

# Prompt stateProvince

`stateProvince` (str): Extract the state, province, or equivalent first-level administrative division where the specimen was collected. Return the full, standard name.

✅ Include:
- US states: 'California', 'Texas', 'New York'
- Canadian provinces and territories: 'Ontario', 'British Columbia', 'Yukon'
- Other first-level divisions: 'Coahuila' (Mexico), 'Paraná' (Brazil), 'New South Wales' (Australia), 'Baden-Württemberg' (Germany)
- Inferred from locality or coordinates: e.g., 'San Francisco Bay' → 'California', 'Toronto' → 'Ontario'
- Historical names if that is what is written on the label

❌ DO NOT include:
- Country names — those belong in `country`
- Counties, parishes, or municipalities — those belong in `county` or `municipality`
- Specific localities, landmarks, or coordinates — those belong in `locality` or coordinate fields
- Abbreviations or acronyms (e.g., 'CA', 'BC', 'ON') — expand to full name

Normalization: Return the full standard name. Expand common abbreviations ('CA' → 'California', 'BC' → 'British Columbia'). If multiple states/provinces are listed, include all of them. If the state/province is not stated but can be reliably inferred from the locality or coordinates, return the inferred value. If no state/province information is available or inference is ambiguous, return an empty string.

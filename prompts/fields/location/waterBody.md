---
name: waterBody
description: Extract the name of the specific body of water where the specimen was collected. This refers to a named water feature, not general habitat or proximity descriptions
---

# Prompt

`waterBody` (str): Extract the name of the specific body of water where the specimen was collected. This refers to a named water feature, not general habitat or proximity descriptions.

✅ Include:
- Named lakes and reservoirs: 'Lake Michigan', 'Lac Saint-François', 'Lake Tahoe'
- Rivers and streams: 'Mississippi River', 'Rio Grande', 'Cedar Creek'
- Oceans and seas: 'Pacific Ocean', 'Mediterranean Sea', 'Caribbean Sea'
- Bays, estuaries, and sounds: 'Chesapeake Bay', 'San Francisco Bay', 'Hudson Sound'
- Springs, ponds, and canals: 'Blue Spring', 'Crystal Pond', 'Erie Canal'
- Fjords, gulfs, and straits: 'Sognefjord', 'Gulf of Mexico', 'Bering Strait'
- Water bodies mentioned with proximity indicators: 'near Lake X' → 'Lake X', 'mouth of River Y' → 'River Y'

❌ DO NOT include:
- General habitat or environmental terms: 'wetland', 'riparian zone', 'aquatic', 'beach', 'shoreline', 'stream bank', 'near water'
- Place names, road names, or land-based geographic features — those belong in `locality`
- Water quality or depth descriptors (e.g., 'deep water', 'brackish water', 'tidal flat')
- Directional or relative water references without a specific name (e.g., 'coastal waters', 'open ocean')

Normalization: Return the name exactly as written on the label. Strip proximity or contextual labels (e.g., 'collected near Lake Tahoe' → 'Lake Tahoe'). If multiple water bodies are listed, include all of them. If no water body is stated, return an empty string.

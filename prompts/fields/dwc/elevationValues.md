`elevationValues` (list[float]): Extract the numeric elevation value(s). A single value indicates a point elevation; two values indicate an elevation range (min and max). The same elevation may be reported in different unit systems — include all numeric values in the order they appear.

✅ Include:
- Single values: '1500 m' → [1500.0]
- Elevation ranges: '1000-1500 m' → [1000.0, 1500.0]
- Dual-unit values: '5000 ft (1524 m)' → [5000.0, 1524.0]
- Decimal values: '1500.5 m' → [1500.5]
- Values with commas: '1,500 m' → [1500.0] (strip commas)

❌ DO NOT include:
- Units — those belong in `elevationUnits`
- Labels or prefixes (e.g., 'elev.', 'alt.', 'altitude:') — extract only the numbers
- Uncertainty markers (e.g., '~', '?', 'ca.') — those belong in `elevationEstimated`
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`
- Depth below sea level (negative values) unless explicitly given as elevation above sea level
- Habitat or environmental descriptors (e.g., 'high altitude', 'mountainous')

Normalization: Return only the numeric values as floats. Strip commas, units, labels, and uncertainty markers. Do not convert between unit systems (e.g., do not convert feet to meters — extract both values as-is).

Examples:
- '1500 m' → [1500.0]
- '4921 ft' → [4921.0]
- '1000-1500 m' → [1000.0, 1500.0]
- '1200 m - 1800 m' → [1200.0, 1800.0]
- '5000 ft (1524 m)' → [5000.0, 1524.0]
- 'ca. 1500 m' → [1500.0] (strip 'ca.')
- 'elev. ~3000 m' → [3000.0] (strip 'elev.' and '~')
- '1500 m?' → [1500.0] (strip '?')
- 'alt. 2000 ft' → [2000.0]
- '3000 meters' → [3000.0]
- '1,500 m' → [1500.0]

If no elevation values are present, return an empty list.

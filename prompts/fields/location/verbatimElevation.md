---
name: verbatimElevation
description: Extract the verbatim elevation or altitude at which the specimen was collected
---

# Prompt

`verbatimElevation` (str): Extract the verbatim elevation or altitude at which the specimen was collected. Preserve the text exactly as written — do not reformat, convert units, or normalize.

✅ Include:
- Numeric values with units: '1500 m', '4921 ft', '2000 meters'
- Elevation ranges: '1000-1500 m', '3000-3500 ft', '1200 m - 1800 m'
- Labels and prefixes: 'elev. 1500 m', 'alt. 2000 ft', 'altitude: 3000'
- Approximate or estimated elevations: 'ca. 1500 m', 'approx. 2000 ft', '1500 m?'
- Elevation expressed in different unit systems: '5000 ft (1524 m)', '3000 m / 9843 ft'

❌ DO NOT include:
- Latitude or longitude values — those belong in `verbatimLatitude`/`verbatimLongitude`
- Depth below sea level or water surface (unless explicitly given as elevation above sea level)
- Habitat or environmental descriptors (e.g., 'high altitude', 'mountainous', 'lowland')
- Coordinates or grid references (e.g., UTM northing/easting values) — those belong in coordinate fields
- Labels that are not part of the elevation string itself (e.g., 'Elevation:', 'Altitude:') — extract only the value

Normalization: Return the value exactly as written on the label. Do not convert units (e.g., keep '4921 ft', do not change to '1500 m'). Preserve ranges, labels, and uncertainty markers as they appear. If no elevation information is present, return an empty string.

# Prompt

`elevationEstimated` (bool): Determine whether the elevation value is an estimate rather than a precise measurement. Look for explicit uncertainty markers near the elevation value.

✅ Return `true` if you find:
- Approximation words: 'approx.', 'approximately', 'est.', 'estimated', 'ca.', 'circa', 'about', 'around'
- Uncertainty symbols: '~' (tilde), '?' (question mark) adjacent to the elevation
- Phrases indicating estimation: 'roughly', 'about', 'some', 'near'

❌ Return `false` if:
- The elevation is stated as a precise value with no uncertainty markers
- The elevation is a clear numeric value or range without qualifiers

Examples:
- 'ca. 1500 m' → `true`
- 'approx. 2000 ft' → `true`
- 'elev. ~3000 m' → `true`
- '1500 m?' → `true`
- '1500 m' → `false`
- '1000-1500 m' → `false` (a range is not an estimate)
- 'alt. 2000 ft' → `false`

If no elevation information is present on the label, return an empty string.

# Prompt

`elevationUnits` (list[str]): Extract the unit(s) associated with each elevation value. If multiple elevation values are present (e.g., a range, or the same elevation in different unit systems), provide a matching unit for each value in the same order.

✅ Include:
- Metric units: 'm', 'meters', 'metres', 'km'
- Imperial units: 'ft', 'feet', 'f', 'asl', 'asf'
- Other units: 'masl' (meters above sea level), 'm asl', 'above sea level'

❌ DO NOT include:
- Labels or prefixes (e.g., 'elev.', 'alt.', 'altitude') — these are not units
- Numeric values — those belong in `elevationValues`
- Uncertainty markers (e.g., '~', '?', 'ca.') — those belong in `elevationEstimated`

Normalization: Normalize units to the abbreviation form when possible (e.g., 'meters' → 'm', 'feet' → 'ft'). Preserve the original text if the unit is ambiguous or non-standard.

Examples:
- '1500 m' → ['m']
- '4921 ft' → ['ft']
- '1000-1500 m' → ['m'] (single unit applies to the range)
- '5000 ft (1524 m)' → ['ft', 'm'] (two values, two units)
- '3000 meters' → ['m'] (normalized)
- '2000 f' → ['f'] (preserved as written)
- '1500 m asl' → ['m'] ('asl' is a qualifier, not a separate unit)

If no elevation units are present, return an empty list.

# Prompt

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

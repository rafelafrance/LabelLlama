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

---
name: decimalLatitude
description: Extract the decimal latitude at which the specimen was collected
---

# Prompt

`decimalLatitude` (float): Extract the decimal latitude at which the specimen was collected. Return only the plain numeric value as a decimal number.

✅ Include:
- Decimal degree values: 45.1234, -33.8688, 0.0
- Negative values for Southern Hemisphere latitudes (e.g., -33.8688)
- Positive values for Northern Hemisphere latitudes (e.g., 45.1234)
- Values with varying precision (e.g., 45.1, 45.123456)

❌ DO NOT include:
- Labels or prefixes (e.g., 'Lat:', 'latitude', 'lat.', 'LAT') — extract only the number
- Compass direction indicators (e.g., 'N', 'S') — convert to sign (+/-) instead
- Degrees/minutes/seconds (DMS) or degrees/minutes (DM) formats (e.g., '45°12'34"N') — those belong in `verbatimLatitude`
- Longitude values — those belong in `decimalLongitude`
- Elevation or altitude values
- Uncertainty or precision notes (e.g., '±0.01', 'approx.')

Normalization: Return only the plain decimal number. Convert hemisphere indicators to signs ('45.1234 N' → 45.1234, '33.8688 S' → -33.8688). Latitude must fall between -90.0 and 90.0 degrees. If no latitude is present, return an empty string.

---
name: decimalLongitude
description: Extract the decimal longitude at which the specimen was collected
module: llama/fields/location/decimalLongitude.py
---

# Prompt decimalLongitude

`decimalLongitude` (float): Extract the decimal longitude at which the specimen was collected. Return only the plain numeric value as a decimal number.

✅ Include:
- Decimal degree values: -118.2437, 121.4737, 0.0
- Negative values for Western Hemisphere longitudes (e.g., -118.2437)
- Positive values for Eastern Hemisphere longitudes (e.g., 121.4737)
- Values with varying precision (e.g., -93.5, 121.473789)

❌ DO NOT include:
- Labels or prefixes (e.g., 'Lon:', 'longitude', 'long.', 'LONG') — extract only the number
- Compass direction indicators (e.g., 'E', 'W') — convert to sign (+/-) instead
- Degrees/minutes/seconds (DMS) or degrees/minutes (DM) formats (e.g., '93°34'05"W') — those belong in `verbatimLongitude`
- Latitude values — those belong in `decimalLatitude`
- Elevation or altitude values
- Uncertainty or precision notes (e.g., '±0.01', 'approx.')

Normalization: Return only the plain decimal number. Convert hemisphere indicators to signs ('121.4737 E' → 121.4737, '118.2437 W' → -118.2437). Longitude must fall between -180.0 and 180.0 degrees. If no longitude is present, return an empty string.

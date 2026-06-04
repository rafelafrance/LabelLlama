---
name: verbatimLatitude
description: Extract the verbatim latitude at which the specimen was collected
---

# Prompt

`verbatimLatitude` (str): Extract the verbatim latitude at which the specimen was collected. Preserve the value exactly as written — do not reformat, convert, or normalize.

✅ Include:
- Decimal degrees: '45.1234', '-33.8688', '0.0'
- Degrees/minutes/seconds (DMS): '45°12'34"N', '33°52'08"S'
- Degrees/minutes (DM): '45°12.5'N', '-33°52.133'
- Hemisphere indicators: 'N', 'S', '+', '-', or explicit labels ('North', 'South')
- TRS (Township/Range/Section) coordinates: 'T12N R5E S14'
- UTM coordinates: '15N 500000E 4500000N' (latitude component)
- Coordinate pairs if latitude and longitude are combined: '45.1234, -93.5678' — extract only the latitude portion

❌ DO NOT include:
- Longitude values — those belong in `verbatimLongitude`
- Elevation or altitude values
- Geodetic datum references (e.g., 'WGS84', 'NAD83') — those belong in `geodeticDatum`
- Coordinate labels themselves (e.g., 'Lat:', 'Latitude:', 'lat.', 'LAT') — extract only the value
- Uncertain or estimated coordinates marked as such (e.g., 'approx. 45°N') — extract the value but note uncertainty if part of the coordinate string
- Coordinates outside the valid latitude range (-90.0 to 90.0 degrees)

Normalization: Return the value exactly as written on the label. Do not convert DMS to decimal, add/remove hemisphere indicators, or reorder components. If no latitude is present, return an empty string.

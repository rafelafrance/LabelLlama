---
name: verbatimLongitude
description: Extract the verbatim longitude at which the specimen was collected
---

# Prompt verbatimLongitude

`verbatimLongitude` (str): Extract the verbatim longitude at which the specimen was collected. Preserve the value exactly as written — do not reformat, convert, or normalize.

✅ Include:
- Decimal degrees: '-93.5678', '144.9631', '0.0'
- Degrees/minutes/seconds (DMS): '93°34'05"W', '144°57'47"E'
- Degrees/minutes (DM): '93°34.083'W', '144°57.787'
- Hemisphere indicators: 'E', 'W', '+', '-', or explicit labels ('East', 'West')
- TRS (Township/Range/Section) coordinates: 'T12N R5E S14'
- UTM coordinates: '15N 500000E 4500000N' (longitude/easting component)
- Coordinate pairs if latitude and longitude are combined: '45.1234, -93.5678' — extract only the longitude portion

❌ DO NOT include:
- Latitude values — those belong in `verbatimLatitude`
- Elevation or altitude values
- Geodetic datum references (e.g., 'WGS84', 'NAD83') — those belong in `geodeticDatum`
- Coordinate labels themselves (e.g., 'Long:', 'Longitude:', 'long.', 'LONG') — extract only the value
- Uncertain or estimated coordinates marked as such (e.g., 'approx. 93°W') — extract the value but note uncertainty if part of the coordinate string
- Coordinates outside the valid longitude range (-180.0 to 180.0 degrees)

Normalization: Return the value exactly as written on the label. Do not convert DMS to decimal, add/remove hemisphere indicators, or reorder components. If no longitude is present, return an empty string.

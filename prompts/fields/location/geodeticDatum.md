---
name: geodeticDatum
description: Extract the geodetic datum used for the latitude, longitude, TRS, or UTM coordinates. The datum defines the reference frame and ellipsoid model for the coordinates
---

# geodeticDatum

`geodeticDatum` (str): Extract the geodetic datum used for the latitude, longitude, TRS, or UTM coordinates. The datum defines the reference frame and ellipsoid model for the coordinates.

✅ Include:
- Standard global and regional datums: 'WGS84', 'WGS 84', 'NAD27', 'NAD83', 'ED50', 'ETRS89'
- Datum codes and abbreviations: 'GDA94', 'CGCS2000', 'RGF93', 'IERS2010'
- Full datum names: 'World Geodetic System 1984', 'North American Datum 1983'
- Datum versions or realizations if specified: 'NAD83(2011)', 'WGS84 (G2139)', 'GDA2020'

❌ DO NOT include:
- Coordinate values themselves — those belong in `verbatimLatitude`, `verbatimLongitude`, `decimalLatitude`, `decimalLongitude`
- Map projections or coordinate reference systems (e.g., 'UTM Zone 15N', 'Mercator', 'Albers', 'State Plane') — those are projections, not datums
- Coordinate labels or prefixes (e.g., 'Datum:', 'Geodetic:', 'GD') — extract only the value
- Coordinate uncertainty or accuracy notes (e.g., '±100m', 'approximate', 'GPS accuracy: 5m')

Normalization: Return the datum name or code exactly as written. Do not expand abbreviations or change formatting. If multiple datums are listed, include all of them. If no datum is stated, return an empty string.

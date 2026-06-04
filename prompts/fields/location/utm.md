---
name: utm
description: Extract the full Universal Transverse Mercator (UTM) coordinate string from the label. UTM coordinates consist of a zone, northing, and easting values used to pinpoint locations on the Earth's surface
---

# utm

`utm` (str): Extract the full Universal Transverse Mercator (UTM) coordinate string from the label. UTM coordinates consist of a zone, northing, and easting values used to pinpoint locations on the Earth's surface.

✅ Include:
- Complete UTM strings with zone, northing, and easting (e.g., '33T 500000 4649776', 'Zone 11S; 3845372N 0729522E')
- UTM with explicit N/E labels (e.g., 'Z12 N7874900 E768500', '3845372N 0729522E')
- UTM with decimal precision (e.g., '11S 316745.14 3542301.90')
- UTM in any format or case as written on the label

❌ DO NOT include:
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`
- TRS coordinates — those belong in `trs` (e.g., 'T4N R25E S36' is TRS, not UTM)
- Other coordinate systems or grid references (e.g., MGRS, state plane, British National Grid)
- Habitat or locality descriptions that are not UTM coordinates
- Labels or prefixes (e.g., 'UTM:', 'Coordinates:') — extract only the coordinate string

Normalization: Preserve the text exactly as written — do not reformat, reorder, or standardize the UTM string. Keep all spacing, punctuation, capitalization, and decimal precision as it appears on the label.

Examples:
- '33T 500000 4649776' → '33T 500000 4649776'
- 'Zone 11S; 3845372N 0729522E' → 'Zone 11S; 3845372N 0729522E'
- 'Z12 N7874900 E768500' → 'Z12 N7874900 E768500'
- '11S 316745.14 3542301.90' → '11S 316745.14 3542301.90'
- 'UTM 33T 500000 4649776' → '33T 500000 4649776'
- 'T4N R25E S36' → '' (this is TRS, not UTM)
- '38.5°N, 122.3°W' → '' (these are lat/lon, not UTM)
- '33T' → '' (incomplete UTM — zone only, no coordinates)

If no UTM information is present, return an empty string.

# utmEasting

`utmEasting` (str): Extract the easting portion of the Universal Transverse Mercator (UTM) coordinates. Easting represents the east-west position within a UTM zone and is typically a 6- or 7-digit number.

✅ Include:
- Standard easting formats (e.g., '509257', '0484145', '642700')
- Easting with 'E' label (e.g., 'E 642700', '509257E', '368.2 E')
- Easting with decimal precision (e.g., '500000.14', '316745.14')
- Easting appearing in any spacing or punctuation style

❌ DO NOT include:
- The 'E' or 'Easting' label — extract only the numeric value
- Northing values — those belong in `utmNorthing` (e.g., '3845372N' is northing, not easting)
- UTM zone values — those belong in `utmZone` (e.g., '33T' is a zone, not easting)
- The full UTM string — that belongs in `utm`
- Longitude values — those belong in `decimalLongitude` (e.g., '122.3°W' is longitude, not easting)
- TRS range values — those belong in `trsRange` (e.g., 'R25E' is TRS range, not UTM easting)

Normalization: Strip the 'E', 'Easting' label and any extra spacing/punctuation. Return only the numeric value, preserving decimal precision and leading zeros as written (e.g., 'E 642700' → '642700', '0484145E' → '0484145'). Easting is never negative — dashes are separators, not minus signs.

Examples:
- 'E 642700' → '642700'
- '509257E' → '509257'
- '0484145E' → '0484145'
- '368.2 E' → '368.2'
- '33T 500000 4649776' → '500000' (easting is first after zone)
- 'Zone 11S; 3845372N 0729522E' → '0729522'
- 'Z12 N7874900 E768500' → '768500'
- '11S 316745.14 3542301.90' → '316745.14' (easting is first when no N/E labels)
- '3845372N' → '' (this is northing, not easting)
- '33T' → '' (this is a zone, not easting)
- '122.3°W' → '' (this is longitude, not easting)
- 'R25E' → '' (this is TRS range, not UTM easting)

If no easting is present, return an empty string.

# utmNorthing

`utmNorthing` (str): Extract the northing portion of the Universal Transverse Mercator (UTM) coordinates. Northing represents the north-south position within a UTM zone and is typically a 7-digit number (smaller in the southern hemisphere).

✅ Include:
- Standard northing formats (e.g., '3845372', '4253279', '3968400')
- Northing with 'N' label (e.g., '3845372N', '4057.6 N', 'N 4253279')
- Northing with decimal precision (e.g., '4649776.14', '3542301.90')
- Northing appearing in any spacing or punctuation style

❌ DO NOT include:
- The 'N' or 'Northing' label — extract only the numeric value
- Easting values — those belong in `utmEasting` (e.g., '509257E' is easting, not northing)
- UTM zone values — those belong in `utmZone` (e.g., '33T' is a zone, not northing)
- The full UTM string — that belongs in `utm`
- Latitude values — those belong in `decimalLatitude` (e.g., '38.5°N' is latitude, not northing)
- TRS township values — those belong in `trsTownship` (e.g., 'T4N' is TRS township, not UTM northing)

Normalization: Strip the 'N', 'Northing' label and any extra spacing/punctuation. Return only the numeric value, preserving decimal precision and leading zeros as written (e.g., '3845372N' → '3845372', '4057.6 N' → '4057.6'). Northing is never negative — dashes are separators, not minus signs.

Examples:
- '3845372N' → '3845372'
- '4057.6 N' → '4057.6'
- '3968400 N' → '3968400'
- 'N 4253279' → '4253279'
- '33T 500000 4649776' → '4649776' (northing is second after zone)
- 'Zone 11S; 3845372N 0729522E' → '3845372'
- 'Z12 N7874900 E768500' → '7874900'
- '11S 316745.14 3542301.90' → '3542301.90' (northing is second when no N/E labels)
- '509257E' → '' (this is easting, not northing)
- '33T' → '' (this is a zone, not northing)
- '38.5°N' → '' (this is latitude, not northing)
- 'T4N' → '' (this is TRS township, not UTM northing)

If no northing is present, return an empty string.

# utmZone

`utmZone` (str): Extract the zone portion of the Universal Transverse Mercator (UTM) coordinates. UTM zones are 6° longitudinal bands numbered 1–60 around the globe, often combined with a latitude band letter (C–X, excluding I and O).

✅ Include:
- Standard zone formats with latitude band (e.g., '10S', '11N', '16P', '33T')
- Zone number alone without latitude band (e.g., '11', '8', '33')
- Zone with explicit labels (e.g., 'Zone 11S', 'Zone 10', 'Z12')
- Northern hemisphere zones (e.g., 'NH' — though rare, preserve as written)

❌ DO NOT include:
- The 'Zone', 'Z', 'Zone.' label — extract only the zone value itself
- Northing values — those belong in `utmNorthing` (e.g., '3845372N' is northing, not a zone)
- Easting values — those belong in `utmEasting` (e.g., '509257E' is easting, not a zone)
- The full UTM string — that belongs in `utm`
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`
- TRS township values — those belong in `trsTownship` (e.g., 'T4N' is TRS township, not a UTM zone)

Normalization: Strip the 'Zone', 'Z', 'Zone.' label and any extra spacing/punctuation. Return only the zone number and latitude band letter (if present), with no space between them (e.g., 'Zone 11S' → '11S', 'Z12' → '12').

Examples:
- '10S' → '10S'
- '11' → '11'
- '8N' → '8N'
- 'Zone 11S' → '11S'
- 'NH' → 'NH'
- '16P' → '16P'
- '33T 500000 4649776' → '33T'
- 'Zone 11S; 3845372N 0729522E' → '11S'
- 'Z12 N7874900 E768500' → '12'
- '11S 316745.14 3542301.90' → '11S'
- '3845372N' → '' (this is northing, not a zone)
- '509257E' → '' (this is easting, not a zone)
- '38.5°N' → '' (this is latitude, not a zone)
- 'T4N' → '' (this is TRS township, not a UTM zone)

If no zone is present, return an empty string.

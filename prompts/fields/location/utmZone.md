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

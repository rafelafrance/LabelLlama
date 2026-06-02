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

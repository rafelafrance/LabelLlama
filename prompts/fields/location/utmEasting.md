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

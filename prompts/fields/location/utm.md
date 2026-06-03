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

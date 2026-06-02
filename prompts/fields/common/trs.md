`trs` (str): Extract the full Township-Range-Section (TRS) coordinate string from the label. TRS is a land survey system used primarily in the United States for describing land parcels.

✅ Include:
- Complete TRS strings with township, range, and section (e.g., 'T4N R25E S36', 'T7S R1W SE 1/4 sec. 33')
- TRS with quadrant subdivisions (e.g., 'NW 1/4 S10', 'SE ¼ of Section 17')
- Quadrangle (quad) names if present (e.g., 'Bodie Quadrangle; T4N R25E S36')
- Partial TRS strings (e.g., 'SW 1/4 sec. 34' — section and quadrant only)
- TRS in any format or case as written on the label

❌ DO NOT include:
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`
- UTM coordinates — those belong in `utmEasting`/`utmNorthing`/`utmZone`
- Other coordinate systems or grid references (e.g., MGRS, state plane)
- Habitat or locality descriptions that are not TRS coordinates
- Labels or prefixes (e.g., 'TRS:', 'Location:') — extract only the coordinate string

Normalization: Preserve the text exactly as written — do not reformat, reorder, or standardize the TRS string. Keep all spacing, punctuation, and capitalization as it appears on the label.

Examples:
- 'T4N R25E S36' → 'T4N R25E S36'
- 'Bodie Quadrangle; T4N R25E S36' → 'Bodie Quadrangle; T4N R25E S36'
- 'T7S, R1W SE 1/4 sec. 33' → 'T7S, R1W SE 1/4 sec. 33'
- 'SW 1/4 sec. 34' → 'SW 1/4 sec. 34'
- 'T41N R15E NW 1/4 S10' → 'T41N R15E NW 1/4 S10'
- '38.5°N, 122.3°W' → '' (these are lat/lon, not TRS)
- 'UTM 33T 500000 4280000' → '' (these are UTM coordinates, not TRS)

If no TRS information is present, return an empty string.

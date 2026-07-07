---
name: trs
description: Extract the full Township-Range-Section (TRS) coordinate string from the label. TRS is a land survey system used primarily in the United States for describing land parcels
module: llama/fields/location/trs.py
---

# Prompt trs

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

# Prompt trsTownship

`trsTownship` (str): Extract the township portion of the Township-Range-Section (TRS) coordinates. Township indicates the north-south position within a survey principal meridian.

✅ Include:
- Standard township formats (e.g., 'T28N', 'T 32 N', 'T.43S')
- Township with explicit labels (e.g., 'Township 4 North', 'Twp. 7S')
- Township values appearing in any spacing or punctuation style

❌ DO NOT include:
- The 'T', 'Twp.', 'Township' prefix — extract only the numeric value and compass direction
- Range values — those belong in `trsRange` (e.g., 'R25E' is range, not township)
- Section values — those belong in `trsSection`
- Quadrangle names — those belong in `trsQuad`
- The full TRS string — that belongs in `trs`
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`

Normalization: Strip the 'T', 'Twp.', 'Township' prefix and all extra spacing/punctuation. Return only the number followed by the compass direction ('N' or 'S'), with no space between them (e.g., 'T 32 N' → '32N', 'T.43S' → '43S').

Examples:
- 'T28N' → '28N'
- 'T 32 N' → '32N'
- 'T.43S' → '43S'
- 'Township 4 North' → '4N'
- 'Twp. 7S' → '7S'
- 'T4N R25E S36' → '4N'
- 'T7S, R1W SE 1/4 sec. 33' → '7S'
- 'R25E S36' → '' (no township present)
- '38.5°N' → '' (this is latitude, not township)

If no township is present, return an empty string.

# Prompt trsRange

`trsRange` (str): Extract the range portion of the Township-Range-Section (TRS) coordinates. Range indicates the east-west position within a survey principal meridian.

✅ Include:
- Standard range formats (e.g., 'R23E', 'R 1 W', 'R.11W')
- Range with explicit labels (e.g., 'Range 15 East', 'Rng. 2W')
- Range values appearing in any spacing or punctuation style

❌ DO NOT include:
- The 'R' or 'Range' prefix — extract only the numeric value and compass direction
- Township values — those belong in `trsTownship` (e.g., 'T4N' is township, not range)
- Section values — those belong in `trsSection`
- Quadrangle names — those belong in `trsQuad`
- The full TRS string — that belongs in `trs`
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`

Normalization: Strip the 'R', 'Range', 'Rng.' prefix and all extra spacing/punctuation. Return only the number followed by the compass direction ('E' or 'W'), with no space between them (e.g., 'R 1 W' → '1W', 'R.11W' → '11W').

Examples:
- 'R23E' → '23E'
- 'R 1 W' → '1W'
- 'R.11W' → '11W'
- 'Range 15 East' → '15E'
- 'Rng. 2W' → '2W'
- 'T4N R25E S36' → '25E'
- 'T7S, R1W SE 1/4 sec. 33' → '1W'
- 'T4N S36' → '' (no range present)
- 'R23E' in 'T4N R23E S36' → '23E'
- '38.5°W' → '' (this is longitude, not range)

If no range is present, return an empty string.

# Prompt trsSection

`trsSection` (str): Extract the section portion of the Township-Range-Section (TRS) coordinates. Section is a one-square-mile parcel within a township, often further divided into quadrant subdivisions (NE, NW, SE, SW) and fractional parts (1/4, 1/16, etc.).

✅ Include:
- Section number alone (e.g., '18', 'S36', 'sec. 33')
- Section with quadrant subdivisions (e.g., 'NW 1/4 S10', 'SE ¼ of Section 17')
- Nested quadrant subdivisions (e.g., 'se1/4 ne1/4 sec 12')
- Section with explicit labels (e.g., 'Section 8', 'section 18', 'sec. 33')

❌ DO NOT include:
- Township values — those belong in `trsTownship` (e.g., 'T4N' is township, not section)
- Range values — those belong in `trsRange` (e.g., 'R25E' is range, not section)
- Quadrangle names — those belong in `trsQuad`
- The full TRS string — that belongs in `trs`
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`

Normalization: Strip the 'S', 'sec', 'sec.', 'Section', 'section' labels. Return the quadrant subdivision (if present), fractional part, and section number as a single string. Normalize quadrant directions to uppercase two-letter abbreviations (e.g., 'se' → 'SE', 'northwest' → 'NW'). Preserve fractional notation as written (e.g., '1/4', '¼').

Examples:
- 'S36' → '36'
- 'sec. 33' → '33'
- 'Section 17' → '17'
- 'NW 1/4 S10' → 'NW 1/4 10'
- 'SE ¼ Section 17' → 'SE ¼ 17'
- 'se1/4 ne1/4 sec 12' → 'SE 1/4 NE 1/4 12'
- 'NW¼ of sec. 8' → 'NW ¼ 8'
- 'section 18' → '18'
- 'T4N R25E S36' → '36'
- 'T4N R25E' → '' (no section present)
- '38.5°N' → '' (this is latitude, not a section)

If no section is present, return an empty string.

# Prompt trsQuad

`trsQuad` (str): Extract the quadrangle (quad) name associated with the TRS coordinates. A quadrangle is the name of a USGS topographic map sheet that covers the collection area. The quad name may appear before or after the township, range, and section values.

✅ Include:
- Standard quad names (e.g., 'Yountville', 'Bodie', 'Chicken Hawk Hill')
- Quad names with scale or format indicators (e.g., 'USGS Wahtoke 7.5 min quad', 'Bodie 7 1/2 quadrangle')
- Quad names with abbreviations (e.g., 'Mt. Ingalls quad.', 'Mt Shasta quadrangle')
- Quad names preceded or followed by TRS coordinates

❌ DO NOT include:
- The township, range, or section values — those belong in `trsTownship`, `trsRange`, `trsSection`
- The full TRS string — that belongs in `trs`
- Latitude or longitude values — those belong in `decimalLatitude`/`decimalLongitude`
- General locality or habitat descriptions that are not quad names
- Labels themselves ('quad', 'quadrangle', 'USGS quad') — extract only the map sheet name

Normalization: Strip the label words 'quad', 'quadrangle', 'quad.', 'map', 'sheet' and any scale indicators (e.g., '7.5 min', '7 1/2'). Preserve the quad name exactly as written, including punctuation like periods in abbreviations (e.g., 'Mt.').

Examples:
- 'USGS Wahtoke 7.5 min quad' → 'Wahtoke'
- 'Yountville Quad' → 'Yountville'
- 'Chicken Hawk Hill quadrangle' → 'Chicken Hawk Hill'
- 'Mt. Ingalls quad.' → 'Mt. Ingalls'
- 'Bodie Quadrangle; T4N R25E S36' → 'Bodie'
- 'T4N R25E S36, Bodie quad' → 'Bodie'
- 'Mt Shasta 7 1/2 quadrangle' → 'Mt Shasta'
- 'T4N R25E S36' → '' (no quad name present)
- 'near Bodie, California' → '' (locality description, not a quad reference)

If no quadrangle is mentioned, return an empty string.

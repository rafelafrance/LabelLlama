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

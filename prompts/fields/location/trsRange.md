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

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

`utmNorthing` (str):
Extract the northing portion of the UTM coordinates. It is a number
(possibly decimal) followed by or preceded by an 'N'.
Examples: '3845372N', '4057.6 N', '3968400 N', 'N 4253279'.
Northing is never negative — dashes are separators, not minus signs.
Return only the numeric value, not the 'N' label.
If no northing is present, return an empty string.

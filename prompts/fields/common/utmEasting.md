`utmEasting` (str):
Extract the easting portion of the UTM coordinates. It is a number
(possibly decimal) followed by or preceded by an 'E'.
Examples: 'E 642700', '509257E', '0484145E', '368.2 E'.
Easting is never negative — dashes are separators, not minus signs.
Return only the numeric value, not the 'E' label.
If no easting is present, return an empty string.

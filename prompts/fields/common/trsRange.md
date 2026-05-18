`trsRange` (str):
Extract the range portion of the TRS coordinates. It will look like 'R23E', 'R 1 W', 'R.11W'.
The letter 'R' followed by digits and an 'E' or 'W' compass direction.
Return only the value without the 'R' prefix.
If no range is present, return an empty string.

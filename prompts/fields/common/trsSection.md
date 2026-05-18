`trsSection` (str):
Extract the section portion of the TRS coordinates. This may include
quadrant subdivisions (e.g., 'NW 1/4', 'SE ¼') and the section number.
Examples: '1/4 S10', 'se1/4 ne1/4 sec 12', 'SE ¼ Section 17',
'NW¼ of sec. 8', 'section 18'.
Return only the section value, not the 'sec' or 'S' label.
If no section is present, return an empty string.

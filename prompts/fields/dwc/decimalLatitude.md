`decimalLatitude` (float):
Extract the decimal latitude at which the specimen was collected.
Return only the numeric value as a decimal number.
Latitude must fall between -90.0 and 90.0 degrees.
    ✅ Include: negative values for Southern Hemisphere (e.g., -33.8688),
        positive values for Northern Hemisphere (e.g., 45.1234, 45.123456).
    ✅ Include: the negative sign (-) for Southern Hemisphere latitudes is imporant.
    ❌ DO NOT include: the label itself (e.g., 'lat.', 'latitude', 'Lat:'),
        compass direction letters (e.g., 'N', 'S'), or the paired longitude value.
    ❌ DO NOT include: degrees/minutes/seconds format (e.g., '45°12'34"') —
        that belongs in verbatimLatitude. Only return a plain decimal number.
Examples: '45.1234', '-33.8688', '0.0', '89.9', '-89.9'.
If no latitude is present, return an empty string.

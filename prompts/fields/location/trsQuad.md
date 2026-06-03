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

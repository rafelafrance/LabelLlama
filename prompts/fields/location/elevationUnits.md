`elevationUnits` (list[str]): Extract the unit(s) associated with each elevation value. If multiple elevation values are present (e.g., a range, or the same elevation in different unit systems), provide a matching unit for each value in the same order.

✅ Include:
- Metric units: 'm', 'meters', 'metres', 'km'
- Imperial units: 'ft', 'feet', 'f', 'asl', 'asf'
- Other units: 'masl' (meters above sea level), 'm asl', 'above sea level'

❌ DO NOT include:
- Labels or prefixes (e.g., 'elev.', 'alt.', 'altitude') — these are not units
- Numeric values — those belong in `elevationValues`
- Uncertainty markers (e.g., '~', '?', 'ca.') — those belong in `elevationEstimated`

Normalization: Normalize units to the abbreviation form when possible (e.g., 'meters' → 'm', 'feet' → 'ft'). Preserve the original text if the unit is ambiguous or non-standard.

Examples:
- '1500 m' → ['m']
- '4921 ft' → ['ft']
- '1000-1500 m' → ['m'] (single unit applies to the range)
- '5000 ft (1524 m)' → ['ft', 'm'] (two values, two units)
- '3000 meters' → ['m'] (normalized)
- '2000 f' → ['f'] (preserved as written)
- '1500 m asl' → ['m'] ('asl' is a qualifier, not a separate unit)

If no elevation units are present, return an empty list.

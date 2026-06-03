`elevationEstimated` (bool): Determine whether the elevation value is an estimate rather than a precise measurement. Look for explicit uncertainty markers near the elevation value.

✅ Return `true` if you find:
- Approximation words: 'approx.', 'approximately', 'est.', 'estimated', 'ca.', 'circa', 'about', 'around'
- Uncertainty symbols: '~' (tilde), '?' (question mark) adjacent to the elevation
- Phrases indicating estimation: 'roughly', 'about', 'some', 'near'

❌ Return `false` if:
- The elevation is stated as a precise value with no uncertainty markers
- The elevation is a clear numeric value or range without qualifiers

Examples:
- 'ca. 1500 m' → `true`
- 'approx. 2000 ft' → `true`
- 'elev. ~3000 m' → `true`
- '1500 m?' → `true`
- '1500 m' → `false`
- '1000-1500 m' → `false` (a range is not an estimate)
- 'alt. 2000 ft' → `false`

If no elevation information is present on the label, return an empty string.

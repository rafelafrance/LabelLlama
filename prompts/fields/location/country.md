`country` (str): Extract the country where the specimen was collected. Return the full, standard English country name.

✅ Include:
- Full country names: 'United States', 'Canada', 'Mexico', 'Japan', 'Brazil'
- Countries inferred from state/province, locality, or coordinates: e.g., 'California' → 'United States', 'Ontario' → 'Canada'
- Historical country names if that is what is written on the label: 'USSR', 'West Germany', 'Czechoslovakia' (preserve as written)
- Oceanic or high-seas collections: 'High Seas', 'International Waters', 'South Pacific Ocean'

❌ DO NOT include:
- Abbreviations or acronyms (e.g., 'USA', 'US', 'CAN', 'MEX') — expand to full name
- State, province, county, or municipality names — those belong in `stateProvince`, `county`, or `municipality`
- Specific localities, landmarks, or coordinates — those belong in `locality` or coordinate fields
- Political subdivisions or territories that are not sovereign nations (e.g., 'Puerto Rico', 'Guam') — map to the sovereign country ('United States') unless specified otherwise

Normalization: Return the standard English full country name. Expand common abbreviations ('USA' → 'United States', 'UK' → 'United Kingdom', 'UK'/'England'/'Scotland' → 'United Kingdom'). If the country is not stated but can be reliably inferred from the state, province, or locality, return the inferred country. If no country information is available or inference is ambiguous, return an empty string.

`municipality` (str): Extract the municipality — the city, town, village, or other populated place where the specimen was collected. Return the full, standard name.

✅ Include:
- Cities, towns, and villages: 'Springfield', 'Toronto', 'Mexico City', 'Kyoto'
- Hamlets, settlements, and populated places: 'Greenwich Village', 'Santa Cruz', 'Ottawa'
- Inferred from locality: e.g., 'Downtown Park' → 'Springfield', 'University of Toronto campus' → 'Toronto'
- Historical municipality names if that is what is written on the label
- Multiple municipalities if listed (e.g., specimens collected across a region)

❌ DO NOT include:
- Country or state/province names — those belong in `country` or `stateProvince`
- County or parish names — those belong in `county`
- Specific localities, landmarks, or coordinates — those belong in `locality` or coordinate fields
- Neighborhoods, districts, or suburbs unless they function as the primary municipality
- Trailing labels like 'City', 'Town', 'Village' — extract only the name

Normalization: Return the full standard name without trailing labels (e.g., 'Springfield City' → 'Springfield'). If multiple municipalities are listed, include all of them. If the municipality is not stated but can be reliably inferred from the locality, return the inferred value. If no municipality information is available or inference is ambiguous, return an empty string.

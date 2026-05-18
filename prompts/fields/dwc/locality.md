`locality` (str):
Extract the locality — the specific place or geographic description where
the specimen was collected. This may include multiple phrases joined by
commas or conjunctions.
    ✅ Include: place names, geographic features, road names, distances
        from towns, landmarks, and field-level descriptions.
    ❌ DO NOT include: TRS coordinates, UTM coordinates, elevation,
        county, state/province, or country — those have their own fields.
    ❌ DO NOT include: habitat descriptions (e.g., 'wetland', 'grassland')
        or associated taxa — those have their own fields.
If no locality is present, return an empty string.

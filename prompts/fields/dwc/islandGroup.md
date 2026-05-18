`islandGroup` (str):
Extract the name of the island group, archipelago, or atoll group where
the specimen was collected.
    ✅ Include: archipelagos ('Galápagos', 'Aleutian Islands', 'Lesser
        Antilles', 'Austral Islands'), island groups ('West Indies',
        'Mariana Islands', 'Bismarck Archipelago'), atoll groups,
        and named clusters of islands.
    ❌ DO NOT include individual island names (e.g., 'Hawaii',
        'Vancouver Island', 'Isla de la Juventud') — those belong to
        island.
    ❌ DO NOT include country, state/province, or other administrative
        divisions — those have their own fields.
    ❌ DO NOT include general locality descriptions — those belong to
        locality.
If no island group is stated, return an empty string.

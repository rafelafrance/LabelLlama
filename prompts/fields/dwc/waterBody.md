`waterBody` (str):
Extract the name of the water body where the specimen was collected.
This refers to a specific named body of water, not general habitat
descriptions.
    ✅ Include: named lakes ('Lake Michigan', 'Lac Saint-François'),
        rivers ('Mississippi River', 'Rio Grande'), oceans/seas
        ('Pacific Ocean', 'Mediterranean Sea'), bays/estuaries
        ('Chesapeake Bay', 'San Francisco Bay'), reservoirs,
        ponds, springs, creeks, streams, canals, and fjords.
    ❌ DO NOT include general habitat terms like 'wetland',
        'stream bank', 'riparian', 'aquatic', 'beach', 'shoreline',
        'near water' — those belong to habitat.
    ❌ DO NOT include place names, road names, or geographic
        features that are not bodies of water — those belong to
        locality.
If no water body is stated, return an empty string.

`habitat` (str):
Extract the habitat or environment where the specimen grows.
Describe the physical conditions and setting, not the location.
    ✅ Include: substrate ('dry sand', 'loamy soil', 'rocky outcrop'),
        vegetation type ('open grassland', 'mixed forest', 'shrubland'),
        hydrology ('wetland', 'stream bank', 'riparian'),
        disturbance ('roadside', 'old field', 'disturbed ground'),
        and life zones ('desert', 'prairie', 'alpine meadow').
    ❌ DO NOT include associated taxa — those belong to associatedTaxa.
    ❌ DO NOT include place names, geographic features, road names,
        or 'near [named place]' — those belong to locality.
    ❌ DO NOT include details about the plant itself (height, color, flowers).
If no habitat information is present, return an empty string.

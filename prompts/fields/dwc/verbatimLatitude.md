`verbatimLatitude` (str):
Extract the verbatim latitude at which the specimen was collected.
Preserve the value exactly as written — it may be decimal degrees
(e.g., '45.1234'), degrees/minutes/seconds (e.g., '45°12'34"N'),
or a coordinate pair. Latitude must fall between -90.0 and 90.0 degrees.
Exclude the label itself (e.g., 'lat.', 'latitude').
If no latitude is present, return an empty string.

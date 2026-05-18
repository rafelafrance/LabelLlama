`infraspecificEpithet` (str):
Extract the infraspecific epithet (subspecies or variety name) from the
scientific name. This is the third name after the genus and species,
e.g., 'var. latifolia' or 'subsp. montana'.
Return only the epithet itself — do not include the rank indicator
('var.', 'subsp.', 'forma', 'f.').
If no infraspecific epithet is present, return an empty string.

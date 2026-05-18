`country` (str):
Extract the country where the specimen was collected.
Return the full country name (e.g., 'United States', 'Canada', 'Mexico'),
not an abbreviation or acronym.
If the country is not stated but can be inferred from the state,
province, or locality, return the inferred country.
If no country information is available, return an empty string.

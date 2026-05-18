`verbatimEventDate` (str):
Extract the verbatim date the specimen was collected.
This may be a full date (e.g., '1995-03-15', '15 March 1995') or a partial
date (e.g., 'Spring 1995', 'July 2001', '1998').
If the date is a range, separate the starting and ending dates with a bar "|".
Exclude the date label itself (e.g., words starting with 'date').
If no collection date is present, return an empty string.

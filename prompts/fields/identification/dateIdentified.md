---
name: dateIdentified
description: Extract the date (or date range) when the specimen was identified, verified, or determined. Preserve the text exactly as written — do not reformat or normalize
---

# dateIdentified

`dateIdentified` (str): Extract the date (or date range) when the specimen was identified, verified, or determined. Preserve the text exactly as written — do not reformat or normalize.

✅ Include:
- Full dates in any format: '1995-03-15', '15 March 1995', 'March 15, 1995'
- Partial dates: 'Spring 1995', 'July 2001', '1998', '1995-03'
- Date ranges: '1995-03-15 to 1995-03-20', '1995-1998'
- Fuzzy or uncertain dates: 'ca. 1995', 'circa 1980', '1995?'
- Dates associated with labels like 'det.', 'det. by', 'id.', 'identified by', 'verified by', 'conf.' — extract only the date value

❌ DO NOT include:
- Collection or observation dates — those belong in `verbatimEventDate`
- Date labels themselves (e.g., 'Date:', 'Identification date:', 'det. date:') — extract only the value
- Determiner or identifier names — those belong in `identifiedBy` (e.g., 'det. by J. Doe on 15 March 2018' → extract '15 March 2018' only)
- Multiple dates for different identification events — use the most recent or primary identification date
- Non-date text mixed into the value (e.g., 'identified by J. Smith on 15 March 1995' → extract '15 March 1995' only)

Normalization: If the date is a range, separate the start and end dates with a bar '|' (e.g., '1995-03-15 to 1995-03-20' → '1995-03-15|1995-03-20'). Otherwise preserve the original text as-is. If no identification date is present, return an empty string.

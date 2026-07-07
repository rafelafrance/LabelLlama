---
name: verbatimEventDate
description: Extract the verbatim date (or date range) when the specimen was collected or observed
module: llama/fields/event/verbatimEventDate.py
---

# Prompt verbatimEventDate

`verbatimEventDate` (str): Extract the verbatim date (or date range) when the specimen was collected or observed. Preserve the text exactly as written — do not reformat or normalize.

✅ Include:
- Full dates in any format: '1995-03-15', '15 March 1995', 'March 15, 1995', '15/03/1995'
- Partial dates: 'Spring 1995', 'July 2001', '1998', '1995-03'
- Date ranges: '1995-03-15 to 1995-03-20', '1995-1998', 'Mar-May 2001'
- Seasonal or qualitative dates: 'late summer', 'flowering season', 'dry season 2010'
- Fuzzy or uncertain dates: 'ca. 1995', 'circa 1980', '1995?', '1995-1996'

❌ DO NOT include:
- Date labels themselves (e.g., 'Date:', 'Collecting date:', 'Collection date:') — extract only the value
- Determination or identification dates (e.g., 'det. 2020', 'identified 15 Jan 2018') — only collection/observation dates
- Multiple dates for different events (e.g., collection + accession) — use the primary collection date
- Non-date text mixed into the value (e.g., 'collected by J. Smith on 15 March 1995' → extract '15 March 1995' only)

Normalization: If the date is a range, separate the start and end dates with a bar '|' (e.g., '1995-03-15 to 1995-03-20' → '1995-03-15|1995-03-20'). Otherwise preserve the original text as-is. If no collection date is present, return an empty string.

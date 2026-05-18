`recordedBy` (str):
Extract the name of the person or people who collected the specimen.
The collector name may appear with labels like 'col.', 'coll.',
'coll. by', or 'collected by'.
    ✅ Include: collector names (individual or institutional), preserving
        the name exactly as written (e.g., 'J. Smith', 'A. B. & C. D.',
        'Smith & Jones', 'USDA Plant Introduction Team').
    ✅ Include: multiple collectors separated by '&', 'and', or commas.
    ❌ DO NOT include: collector labels ('col.', 'coll.', 'collected by').
    ❌ DO NOT include: determiner or identifier names — those belong in
        identifiedBy (e.g., 'det. by', 'id. by', 'verified by').
    ❌ DO NOT include: record numbers or collector accession numbers —
        those belong in recordNumber.
Preserve the name as written — do not expand abbreviations.
If no collector is named, return an empty string.


`trsTownship` (str):
Extract the township portion of the TRS coordinates. It will look like
'T28N', 'T 32 N', or 'T.43'. The letter 'T' followed by digits and an
'N' or 'S' compass direction. Return only the value without the 'T' prefix.
If no township is present, return an empty string.

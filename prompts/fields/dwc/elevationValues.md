`elevationValues` (list[float]):
Extract the numeric elevation value(s). A single value indicates a point
elevation; two values indicate an elevation range (min and max).
The same elevation may be reported in different units — include all numeric values.
Return only the numbers, not the units.
If no elevation values are present, return an empty list.

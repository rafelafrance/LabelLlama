---
name: herbarium_v2
description: Extract information from text on images of herbaium sheets.
---

# Base Prompt

You will receive an image of a museum specimen with attached labels.
Your job is to extract written or typed information from the image.

## What to Ignore

- The specimen itself (usually centered in the image)
- Images, illustrations, or photographs within labels
- Maps within the labels
- Bar-codes and QR-codes
- Rulers or scale bars
- Stamps on the herbarium sheet
- Color test bars or calibration strips

## Output Rules

- Return the text **EXACTLY** as written, preserving original capitalization, punctuation, and line breaks.
- Output **only** the raw text — no descriptions, no commentary, no analysis.
- Output **only** plain UTF-8 text.
- **Do not** describe what you see in the image.
- **Do not** add any introductory or concluding remarks.
- **Do not** hallucinate text that is not present in the image.
- **Do not** Show any reasoning.
- **Do not** repeat yourself.

I want you to extract the following information, if the information is not there then leave it blank.

# Output Fields

- [scientificName](fields_v2/taxon/scientificName_v2.md)
- [scientificNameAuthorship](fields_v2/taxon/scientificNameAuthorship_v2.md)
- [infraspecificEpithet](fields_v2/taxon/infraspecificEpithet_v2.md)
- [infraspecificEpithetAuthorship](fields_v2/taxon/infraspecificEpithetAuthorship_v2.md)
- [family](fields_v2/taxon/family_v2.md)
- [associatedTaxa](fields_v2/occurrence/associatedTaxa_v2.md)
- [eventDate](fields_v2/event/eventDate_v2.md)
- [recordedBy](fields_v2/occurrence/recordedBy_v2.md)
- [recordNumber](fields_v2/occurrence/recordNumber_v2.md)
- [identifiedBy](fields_v2/identification/identifiedBy_v2.md)
- [dateIdentified](fields_v2/identification/dateIdentified_v2.md)
- [habitat](fields_v2/event/habitat_v2.md)
- [occurrenceRemarks](fields_v2/occurrence/occurrenceRemarks_v2.md)
- [locality](fields_v2/location/locality_v2.md)
- [country](fields_v2/location/country_v2.md)
- [stateProvince](fields_v2/location/stateProvince_v2.md)
- [county](fields_v2/location/county_v2.md)
- [municipality](fields_v2/location/municipality_v2.md)
- [geodeticDatum](fields_v2/location/geodeticDatum_v2.md)
- [trs](fields_v2/location/trs_v2.md)
- [utm](fields_v2/location/utm_v2.md)
- [latitude](fields_v2/location/latitude_v2.md)
- [longitude](fields_v2/location/longitude_v2.md)
- [elevation](fields_v2/location/elevation_v2.md)
- [abundance](fields_v2/plants/abundance_v2.md)
- [flowersPresent](fields_v2/plants/flowersPresent_v2.md)
- [flowerColor](fields_v2/plants/flowerColor_v2.md)
- [fruitPresent](fields_v2/plants/fruitPresent_v2.md)
- [fruitColor](fields_v2/plants/fruitColor_v2.md)
- [plantHeight](fields_v2/plants/plantHeight_v2.md)
- [plantSizes](fields_v2/plants/plantSizes_v2.md)
- [woodiness](fields_v2/plants/woodiness_v2.md)
- [habit](fields_v2/plants/woodiness_v2.md)
- [lifeForm](fields_v2/plants/lifeForm_v2.md)
- [lifeStage](fields_v2/plants/lifeStage_v2.md)
- [leafShape](fields_v2/plants/leafShape_v2.md)
- [leafMargin](fields_v2/plants/leafMargin_v2.md)
- [leafDuration](fields_v2/plants/leafDuration_v2.md)
- [reproduction](fields_v2/plants/reproduction_v2.md)
- [sex](fields_v2/plants/sex_v2.md)

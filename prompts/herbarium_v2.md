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

- [scientificName](fields/taxon/scientificName_v1.md)
- [scientificNameAuthorship](fields/taxon/scientificNameAuthorship_v1.md)
- [infraspecificEpithet](fields/taxon/infraspecificEpithet_v1.md)
- [infraspecificEpithetAuthorship](fields/taxon/infraspecificEpithetAuthorship_v1.md)
- [family](fields/taxon/family_v1.md)
- [associatedTaxa](fields/occurrence/associatedTaxa_v1.md)
- [verbatimEventDate](fields/event/verbatimEventDate_v1.md)
- [recordedBy](fields/occurrence/recordedBy_v1.md)
- [recordNumber](fields/occurrence/recordNumber_v1.md)
- [identifiedBy](fields/identification/identifiedBy_v1.md)
- [dateIdentified](fields/identification/dateIdentified_v1.md)
- [habitat](fields/event/habitat_v1.md)
- [occurrenceRemarks](fields/occurrence/occurrenceRemarks_v1.md)
- [locality](fields/location/locality_v1.md)
- [country](fields/location/country_v1.md)
- [stateProvince](fields/location/stateProvince_v1.md)
- [county](fields/location/county_v1.md)
- [municipality](fields/location/municipality_v1.md)
- [geodeticDatum](fields/location/geodeticDatum_v1.md)
- [trs](fields/location/trs_v1.md)
- [utm](fields/location/utm_v1.md)
- [verbatimLatitude](fields/location/verbatimLatitude_v1.md)
- [verbatimLongitude](fields/location/verbatimLongitude_v1.md)
- [verbatimElevation](fields/location/verbatimElevation_v1.md)
- [abundance](fields/plants/abundance_v1.md)
- [flowersPresent](fields/plants/flowersPresent_v1.md)
- [flowerColor](fields/plants/flowerColor_v1.md)
- [fruitPresent](fields/plants/fruitPresent_v1.md)
- [fruitColor](fields/plants/fruitColor_v1.md)
- [plantHeight](fields/plants/plantHeight_v1.md)
- [plantSizes](fields/plants/plantSizes_v1.md)
- [woodiness](fields/plants/woodiness_v1.md)
- [habit](fields/plants/woodiness_v1.md)
- [lifeForm](fields/plants/lifeForm_v1.md)
- [lifeStage](fields/plants/lifeStage_v1.md)
- [leafShape](fields/plants/leafShape_v1.md)
- [leafMargin](fields/plants/leafMargin_v1.md)
- [leafDuration](fields/plants/leafDuration_v1.md)
- [reproduction](fields/plants/reproduction_v1.md)
- [sex](fields/plants/sex_v1.md)

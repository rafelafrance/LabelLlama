---
name: herbarium
description: Extract information from labels on images of herbarium museum specimens.
---

# Base Prompt

You are given text from all labels for a specimen, and you will need to extract
structured botanical and collection metadata from herbarium label text.

You are processing OCRed or transcribed herbarium sheet labels and extracts
containing Darwin Core fields (taxonomy, geolocation, collection event) plus
plant-specific morphological data (phenology, habit, life form, etc.).

Extraction rules:

- **Verbatim fidelity**: Preserve the original text exactly as it appears on the
  label. Do not expand abbreviations, correct spelling, normalize punctuation,
  add/remove whitespace, or rephrase in any way.
- **No inference**: Only extract information explicitly present in the source text.
  Do not infer, summarize, categorize, or add any new information.
- **Missing data**: If a field cannot be found in the text, return the default
  value defined for that field.
- **Plain text output**: Return raw UTF-8 text only. Do not include HTML tags or
  entities, Markdown formatting, MATHML, or any other markup.
- **No hallucination**: Never fabricate data not present in the source.

Extract the following fields from the given text.

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

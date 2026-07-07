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

- [scientificName](taxon/scientificName_v1.md)
- [scientificNameAuthorship](taxon/scientificNameAuthorship_v1.md)
- [infraspecificEpithet](taxon/infraspecificEpithet_v1.md)
- [infraspecificEpithetAuthorship](taxon/infraspecificEpithetAuthorship_v1.md)
- [family](taxon/family_v1.md)
- [associatedTaxa](occurrence/associatedTaxa_v1.md)
- [verbatimEventDate](event/verbatimEventDate_v1.md)
- [recordedBy](occurrence/recordedBy_v1.md)
- [recordNumber](occurrence/recordNumber_v1.md)
- [identifiedBy](identification/identifiedBy_v1.md)
- [dateIdentified](identification/dateIdentified_v1.md)
- [habitat](event/habitat_v1.md)
- [occurrenceRemarks](occurrence/occurrenceRemarks_v1.md)
- [locality](location/locality_v1.md)
- [country](location/country_v1.md)
- [stateProvince](location/stateProvince_v1.md)
- [county](location/county_v1.md)
- [municipality](location/municipality_v1.md)
- [geodeticDatum](location/geodeticDatum_v1.md)
- [trs](location/trs_v1.md)
- [utm](location/utm_v1.md)
- [verbatimLatitude](location/verbatimLatitude_v1.md)
- [verbatimLongitude](location/verbatimLongitude_v1.md)
- [verbatimElevation](location/verbatimElevation_v1.md)
- [abundance](plants/abundance_v1.md)
- [flowersPresent](plants/flowersPresent_v1.md)
- [flowerColor](plants/flowerColor_v1.md)
- [fruitPresent](plants/fruitPresent_v1.md)
- [fruitColor](plants/fruitColor_v1.md)
- [plantHeight](plants/plantHeight_v1.md)
- [plantSizes](plants/plantSizes_v1.md)
- [woodiness](plants/woodiness_v1.md)
- [habit](plants/woodiness_v1.md)
- [lifeForm](plants/lifeForm_v1.md)
- [lifeStage](plants/lifeStage_v1.md)
- [leafShape](plants/leafShape_v1.md)
- [leafMargin](plants/leafMargin_v1.md)
- [leafDuration](plants/leafDuration_v1.md)
- [reproduction](plants/reproduction_v1.md)
- [sex](plants/sex_v1.md)

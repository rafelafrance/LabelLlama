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

- [scientificName](taxon/scientificName.md)
- [scientificNameAuthorship](taxon/scientificNameAuthorship.md)
- [infraspecificEpithet](taxon/infraspecificEpithet.md)
- [infraspecificEpithetAuthorship](taxon/infraspecificEpithetAuthorship.md)
- [family](taxon/family.md)
- [associatedTaxa](occurrence/associatedTaxa.md)
- [verbatimEventDate](event/verbatimEventDate.md)
- [recordedBy](occurrence/recordedBy.md)
- [recordNumber](occurrence/recordNumber.md)
- [identifiedBy](identification/identifiedBy.md)
- [dateIdentified](identification/dateIdentified.md)
- [habitat](event/habitat.md)
- [occurrenceRemarks](occurrence/occurrenceRemarks.md)
- [locality](location/locality.md)
- [country](location/country.md)
- [stateProvince](location/stateProvince.md)
- [county](location/county.md)
- [municipality](location/municipality.md)
- [geodeticDatum](location/geodeticDatum.md)
- [trs](location/trs.md)
- [utm](location/utm.md)
- [verbatimLatitude](location/verbatimLatitude.md)
- [verbatimLongitude](location/verbatimLongitude.md)
- [verbatimElevation](location/verbatimElevation.md)
- [abundance](plants/abundance.md)
- [flowersPresent](plants/flowersPresent.md)
- [flowerColor](plants/flowerColor.md)
- [fruitPresent](plants/fruitPresent.md)
- [fruitColor](plants/fruitColor.md)
- [plantHeight](plants/plantHeight.md)
- [plantSizes](plants/plantSizes.md)
- [woodiness](plants/woodiness.md)
- [habit](plants/woodiness.md)
- [lifeForm](plants/lifeForm.md)
- [lifeStage](plants/lifeStage.md)
- [leafShape](plants/leafShape.md)
- [leafMargin](plants/leafMargin.md)
- [leafDuration](plants/leafDuration.md)
- [reproduction](plants/reproduction.md)
- [sex](plants/sex.md)

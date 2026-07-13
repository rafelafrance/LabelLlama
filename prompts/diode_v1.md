---
name: diode
description: Extract information from labels on images of Odonata museum specimens.
---

# Base Prompt

You will be given OCRed text, and you need to extract
structured biological and collection metadata from the label text.
The target fields are Darwin Core fields (taxonomy, geolocation, collection event)
and fields more commonly found on insect labels like (suborder).

Extraction rules:

- **Verbatim fidelity**: Preserve the original text exactly as it appears on the
  label. Do not expand abbreviations, correct spelling, normalize punctuation,
  add/remove white space, or rephrase in any way.
- **No inference**: Only extract information explicitly present in the source text.
  Do not infer, summarize, categorize, or add any new information.
- **Missing data**: If a field cannot be found in the text, return the default
  value defined for that field.
- **Plain text output**: Return raw UTF-8 text only. Do not include HTML tags or
  entities, Markdown formatting, MATHML, or any other markup.
- **Minimal structure**: Don't add surrounding quotes, parentheses, brackets, or braces.
- **No hallucination**: Never fabricate data not present in the source.

Extract the following fields from the given text.

# Output Fields

- [scientificName](taxon/scientificName_v1.md)
- [scientificNameAuthorship](taxon/scientificNameAuthorship_v1.md)
- [verbatimEventDate](event/verbatimEventDate_v1.md)
- [institutionCode](record_level/institutionCode_v1.md)
- [collectionCode](record_level/collectionCode_v1.md)
- [catalogNumber](occurrence/catalogNumber_v1.md)
- [sex](occurrence/sex_v1.md)
- [lifeStage](insects/lifeStage_v1.md)
- [verbatimLatitude](location/verbatimLatitude_v1.md)
- [decimalLatitude](location/decimalLatitude_v1.md)
- [verbatimLongitude](location/verbatimLongitude_v1.md)
- [decimalLongitude](location/decimalLongitude_v1.md)
- [recordedBy](occurrence/recordedBy_v1.md)
- [recordNumber](occurrence/recordNumber_v1.md)
- [identifiedBy](identification/identifiedBy_v1.md)
- [identifiedByID](identification/identifiedByID_v1.md)
- [dateIdentified](identification/dateIdentified_v1.md)
- [locality](location/locality_v1.md)
- [country](location/country_v1.md)
- [stateProvince](location/stateProvince_v1.md)
- [county](location/county_v1.md)
- [municipality](location/municipality_v1.md)
- [waterBody](location/waterBody_v1.md)
- [habitat](event/habitat_v1.md)
- [occurrenceRemarks](occurrence/occurrenceRemarks_v1.md)

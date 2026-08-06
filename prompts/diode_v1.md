---
name: diode_v1
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

# LLM Fields

- [scientificName](fields_v1/taxon/scientificName_v1.md)
- [scientificNameAuthorship](fields_v1/taxon/scientificNameAuthorship_v1.md)
- [verbatimEventDate](fields_v1/event/verbatimEventDate_v1.md)
- [institutionCode](fields_v1/record_level/institutionCode_v1.md)
- [collectionCode](fields_v1/record_level/collectionCode_v1.md)
- [catalogNumber](fields_v1/occurrence/catalogNumber_v1.md)
- [sex](fields_v1/occurrence/sex_v1.md)
- [lifeStage](fields_v1/insects/lifeStage_v1.md)
- [verbatimLatitude](fields_v1/location/verbatimLatitude_v1.md)
- [decimalLatitude](fields_v1/location/decimalLatitude_v1.md)
- [verbatimLongitude](fields_v1/location/verbatimLongitude_v1.md)
- [decimalLongitude](fields_v1/location/decimalLongitude_v1.md)
- [recordedBy](fields_v1/occurrence/recordedBy_v1.md)
- [recordNumber](fields_v1/occurrence/recordNumber_v1.md)
- [identifiedBy](fields_v1/identification/identifiedBy_v1.md)
- [identifiedByID](fields_v1/identification/identifiedByID_v1.md)
- [dateIdentified](fields_v1/identification/dateIdentified_v1.md)
- [locality](fields_v1/location/locality_v1.md)
- [country](fields_v1/location/country_v1.md)
- [stateProvince](fields_v1/location/stateProvince_v1.md)
- [county](fields_v1/location/county_v1.md)
- [municipality](fields_v1/location/municipality_v1.md)
- [waterBody](fields_v1/location/waterBody_v1.md)
- [habitat](fields_v1/event/habitat_v1.md)
- [occurrenceRemarks](fields_v1/occurrence/occurrenceRemarks_v1.md)

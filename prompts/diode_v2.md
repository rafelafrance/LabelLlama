---
name: diode_v2
description: Extract information from labels on images of Odonata museum specimens.
---

# System Message

You will be given OCR text transcribed from labels attached to an Odonata museum specimen.

Extract structured biological, collection, identification, and locality metadata from the label text.

Use only information explicitly present in the OCR text. Do not infer, normalize, or fill missing values using outside knowledge.

## Output Rules

- Return only valid JSON matching the provided schema.
- Do not include commentary, explanations, Markdown, or reasoning.
- If a field is absent, illegible, uncertain, or not supported by the OCR text, return an empty string.
- Preserve the original wording, spelling, capitalization, punctuation, symbols, and abbreviations when extracting values.
- Do not include field labels such as `det.`, `leg.`, `coll.`, `date`, `lat`, `long`, `sex`, or `catalog no.` unless they are part of the actual value.
- Treat all labels in the OCR text as belonging to the same specimen record.
- If multiple compatible values are present for the same field, join them with ` | `.
- Do not invent taxon names, people, dates, coordinates, geography, institution codes, or catalog numbers.

Extract the requested fields from the OCR text. Leave missing fields blank.

# LLM Fields

- [scientificName](../llama/llm_fields/taxon/scientificName.py)
- [scientificNameAuthorship](../llama/llm_fields/taxon/scientificNameAuthorship.py)
- [verbatimEventDate](../llama/llm_fields/event/verbatimEventDate.py)
- [institutionCode](../llama/llm_fields/record_level/institutionCode.py)
- [collectionCode](../llama/llm_fields/record_level/collectionCode.py)
- [catalogNumber](../llama/llm_fields/occurrence/catalogNumber.py)
- [sex](../llama/llm_fields/occurrence/sex.py)
- [lifeStage](../llama/llm_fields/insects/lifeStage.py)
- [verbatimLatitude](../llama/llm_fields/location/verbatimLatitude.py)
- [decimalLatitude](../llama/llm_fields/location/decimalLatitude.py)
- [verbatimLongitude](../llama/llm_fields/location/verbatimLongitude.py)
- [decimalLongitude](../llama/llm_fields/location/decimalLongitude.py)
- [recordedBy](../llama/llm_fields/occurrence/recordedBy.py)
- [recordNumber](../llama/llm_fields/occurrence/recordNumber.py)
- [identifiedBy](../llama/llm_fields/identification/identifiedBy.py)
- [identifiedByID](../llama/llm_fields/identification/identifiedByID.py)
- [dateIdentified](../llama/llm_fields/identification/dateIdentified.py)
- [locality](../llama/llm_fields/location/locality.py)
- [country](../llama/llm_fields/location/country.py)
- [stateProvince](../llama/llm_fields/location/stateProvince.py)
- [county](../llama/llm_fields/location/county.py)
- [municipality](../llama/llm_fields/location/municipality.py)
- [waterBody](../llama/llm_fields/location/waterBody.py)
- [habitat](../llama/llm_fields/event/habitat.py)
- [occurrenceRemarks](../llama/llm_fields/occurrence/occurrenceRemarks.py)

# Calculated Fields

- [eventDate](../llama/calc_fields/event/eventDate.py)
- [country](../llama/calc_fields/location/country.py)
- [locality](../llama/calc_fields/location/locality.py)

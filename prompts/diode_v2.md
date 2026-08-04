---
name: diode_v2
description: Extract information from labels on images of Odonata museum specimens.
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
- Stamps on the sheet
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

- [scientificName](taxon/scientificName_v2.md)
- [scientificNameAuthorship](taxon/scientificNameAuthorship_v2.md)
- [verbatimEventDate](event/verbatimEventDate_v2.md)
- [institutionCode](record_level/institutionCode_v2.md)
- [collectionCode](record_level/collectionCode_v2.md)
- [catalogNumber](occurrence/catalogNumber_v2.md)
- [sex](occurrence/sex_v2.md)
- [lifeStage](insects/lifeStage_v2.md)
- [verbatimLatitude](location/verbatimLatitude_v2.md)
- [decimalLatitude](location/decimalLatitude_v2.md)
- [verbatimLongitude](location/verbatimLongitude_v2.md)
- [decimalLongitude](location/decimalLongitude_v2.md)
- [recordedBy](occurrence/recordedBy_v2.md)
- [recordNumber](occurrence/recordNumber_v2.md)
- [identifiedBy](identification/identifiedBy_v2.md)
- [identifiedByID](identification/identifiedByID_v2.md)
- [dateIdentified](identification/dateIdentified_v2.md)
- [locality](location/locality_v2.md)
- [country](location/country_v2.md)
- [stateProvince](location/stateProvince_v2.md)
- [county](location/county_v2.md)
- [municipality](location/municipality_v2.md)
- [waterBody](location/waterBody_v2.md)
- [habitat](event/habitat_v2.md)
- [occurrenceRemarks](occurrence/occurrenceRemarks_v2.md)

# Calculated Fields

- [eventDate](../llama/calculated/event/eventDate.py)
- [country](../llama/calculated/location/country.py)
- [locality](../llama/calculated/location/locality.py)
- [recordNumber](../llama/calculated/occurrence/recordNumber.py)

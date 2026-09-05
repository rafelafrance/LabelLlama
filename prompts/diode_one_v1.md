---
name: diode_v2
description: Extract information from labels on images of Odonata museum specimens.
---

# System Message

You are given an image of a museum specimen with attached labels.
Extract written or typed information from the image.

## This includes:

- Typewritten labels
- Handwritten labels
- Small labels and tags
- Printed or handwritten stamps that contain text
- Human-readable catalog numbers printed next to barcodes or QR codes

## What to Ignore

- The specimen itself (usually centered in the image)
- Images, illustrations, or photographs within labels
- Stamps and printed stamps
- Maps within the labels
- Barcodes and QR-codes
- Rulers or scale bars
- Color test bars or calibration strips

## Output Rules

- Output plain UTF-8 text with no Markdown or HTML.
- Return text as written, preserving original capitalization, punctuation, spelling, abbreviations, symbols, and line breaks.
- Preserve the approximate reading order of labels: top-to-bottom, then left-to-right when labels do not clearly form a single column.
- Add 1 newline character (`\n`) when two lines are directly above and below each other on the same label.
- Add 2 newline characters (`\n\n`) when there is vertical white space between lines on the same label.
- Add 2 newline characters (`\n\n`) between separate labels, tags, or stamps.
- Transcribe only visible text. Do not infer missing words, expand abbreviations, normalize dates, or correct spelling.
- If a character or word is illegible, omit it rather than guessing.
- Output the raw text — no descriptions, no commentary, and no analysis.

I want you to extract the following information, if the information is not there then leave it blank.

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

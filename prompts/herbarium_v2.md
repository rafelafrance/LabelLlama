---
name: herbarium_v2
description: Extract information from text on images of herbaium sheets.
---

# System Message

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

# LLM Fields

- [scientificName](../llama/llm_fields/taxon/scientificName.py)
- [scientificNameAuthorship](../llama/llm_fields/taxon/scientificNameAuthorship.py)
- [infraspecificEpithet](../llama/llm_fields/taxon/infraspecificEpithet.py)
- [infraspecificEpithetAuthorship](../llama/llm_fields/taxon/infraspecificEpithetAuthorship.py)
- [family](../llama/llm_fields/taxon/family.py)
- [associatedTaxa](../llama/llm_fields/occurrence/associatedTaxa.py)
- [verbatimEventDate](../llama/llm_fields/event/verbatimEventDate.py)
- [recordedBy](../llama/llm_fields/occurrence/recordedBy.py)
- [recordNumber](../llama/llm_fields/occurrence/recordNumber.py)
- [identifiedBy](../llama/llm_fields/identification/identifiedBy.py)
- [dateIdentified](../llama/llm_fields/identification/dateIdentified.py)
- [habitat](../llama/llm_fields/event/habitat.py)
- [occurrenceRemarks](../llama/llm_fields/occurrence/occurrenceRemarks.py)
- [locality](../llama/llm_fields/location/locality.py)
- [country](../llama/llm_fields/location/country.py)
- [stateProvince](../llama/llm_fields/location/stateProvince.py)
- [county](../llama/llm_fields/location/county.py)
- [municipality](../llama/llm_fields/location/municipality.py)
- [geodeticDatum](../llama/llm_fields/location/geodeticDatum.py)
- [trs](../llama/llm_fields/location/trs.py)
- [utm](../llama/llm_fields/location/utm.py)
- [verbatimLatitude](../llama/llm_fields/location/verbatimLatitude.py)
- [verbatimLongitude](../llama/llm_fields/location/verbatimLongitude.py)
- [verbatimElevation](../llama/llm_fields/location/verbatimElevation.py)
- [abundance](../llama/llm_fields/plants/abundance.py)
- [flowerColor](../llama/llm_fields/plants/flowerColor.py)
- [flowersFacts](../llama/llm_fields/plants/flowerFacts.py)
- [fruitColor](../llama/llm_fields/plants/fruitColor.py)
- [fruitFacts](../llama/llm_fields/plants/fruitFacts.py)
- [plantHeight](../llama/llm_fields/plants/plantHeight.py)
- [plantSizes](../llama/llm_fields/plants/plantSizes.py)
- [woodiness](../llama/llm_fields/plants/woodiness.py)
- [habit](../llama/llm_fields/plants/woodiness.py)
- [lifeForm](../llama/llm_fields/plants/lifeForm.py)
- [lifeStage](../llama/llm_fields/plants/lifeStage.py)
- [leafShape](../llama/llm_fields/plants/leafShape.py)
- [leafMargin](../llama/llm_fields/plants/leafMargin.py)
- [leafDuration](../llama/llm_fields/plants/leafDuration.py)
- [reproduction](../llama/llm_fields/plants/reproduction.py)
- [sex](../llama/llm_fields/plants/sex.py)

# Calculated Fields

- [eventDate](../llama/calc_fields/event/eventDate.py)
- [elevation](../llama/calc_fields/location/elevation.py)
- [country](../llama/calc_fields/location/country.py)
- [locality](../llama/calc_fields/location/locality.py)
- [flowersPresent](../llama/calc_fields/plants/flowersPresent.py)
- [fruitPresent](../llama/calc_fields/plants/fruitPresent.py)
- [family](../llama/calc_fields/taxon/family.py)
- [genus](../llama/calc_fields/taxon/genus.py)
- [specificEpithet](../llama/calc_fields/taxon/specificEpithet.py)

---
name: herbarium_v2
description: Extract information from text on images of herbaium sheets.
---

# System Message

Extract structured biological and collection metadata from OCRed label text attached to herbarium specimens.

## Output Rules

- Output **only** plain UTF-8 text.
- Return **only** valid JSON matching the provided schema.
- Return the text **EXACTLY** as written, preserving the original wording, spelling, capitalization, punctuation, symbols, and abbreviations when extracting values.
- Do not include field labels such as `det.`, `leg.`, `coll.`, `date`, `lat`, `long`, `sex`, or `catalog no.` unless they are part of the actual value.
- Output the raw text — no descriptions, no commentary, no analysis.
- If multiple compatible values are present for the same field, join them with `|`.
- If a field is absent, illegible, uncertain, or not supported by the OCR text, return an empty string.
- Some text may be light, particularly symbols including "♂" and "♀", get that text too.

I want you to extract the following information.

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
- [flowerFacts](../llama/llm_fields/plants/flowerFacts.py)
- [fruitColor](../llama/llm_fields/plants/fruitColor.py)
- [fruitFacts](../llama/llm_fields/plants/fruitFacts.py)
- [plantHeight](../llama/llm_fields/plants/plantHeight.py)
- [plantSizes](../llama/llm_fields/plants/plantSizes.py)
- [woodiness](../llama/llm_fields/plants/woodiness.py)
- [habit](../llama/llm_fields/plants/habit.py)
- [lifeForm](../llama/llm_fields/plants/lifeForm.py)
- [lifeStage](../llama/llm_fields/plants/lifeStage.py)
- [leafShape](../llama/llm_fields/plants/leafShape.py)
- [leafMargin](../llama/llm_fields/plants/leafMargin.py)
- [leafDuration](../llama/llm_fields/plants/leafDuration.py)
- [reproduction](../llama/llm_fields/plants/reproduction.py)
- [sex](../llama/llm_fields/plants/sex.py)

# Required Fields

- scientificName

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

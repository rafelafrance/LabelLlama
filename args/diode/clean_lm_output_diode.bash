#!/bin/bash

uv run llama/clean_llm_output.py \
  --in-file data/diode_geode/diode_imaging_qwen_2026-05-28a.csv \
  --out-file data/diode_geode/diode_imaging_qwen_2026-05-28a_clean.csv \
  --prompt prompts/fields/diode.md \
  --notes "Run a new batch of diode images thru a GPT nano model" \
  --log-file data/diode_geode/diode_imaging_qwen.log


# scientificName
# scientificNameAuthorship
# family
# genus
# subgenus
# specificEpithet
# verbatimEventDate
# locality
# habitat
# sex
# verbatimElevation
# elevationValues
# elevationUnits
# elevationEstimated
# verbatimLatitude
# verbatimLongitude
# collector
# recordNumber
# identifiedBy
# identifiedByID
# occurrenceID
# country
# stateProvince
# county
# municipality
# waterBody
# island
# islandGroup
# occurrenceRemarks

#!/bin/bash

uv run llama/clean_fields.py \
  --parsed-file data/diode/diode_imaging/diode_imaging_qwen_2026-06-01a.csv \
  --clean-file data/diode/diode_imaging/diode_imaging_qwen_2026-06-01a_clean.csv \
  --prompt-md prompts/diode_v2.md \
  --log-file data/diode/diode_imaging/diode_imaging_qwen.log


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

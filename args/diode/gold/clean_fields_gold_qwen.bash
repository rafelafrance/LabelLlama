#!/bin/bash

uv run llama/clean_fields.py \
  --parsed-file data/diode/gold_std/gold_qwen_2026-06-02a.csv \
  --clean-file data/diode/gold_std/gold_qwen_2026-06-02a_clean.csv \
  --prompt-md prompts/diode_v2.md \
  --log-file data/diode/gold_std/gold_std.log


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

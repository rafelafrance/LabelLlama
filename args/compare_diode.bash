#!/bin/bash

uv run ./llama/compare_output.py \
  --imperfect \
  --gold data/diode_geode/Abbott_and_Ware_gold.csv \
  --lm data/diode_geode/rob_gpt_nano_2026-05-14e_cleaned.csv \
  --out-file data/diode_geode/rob_gpt_nano_2026-05-14e.csv

# scientificName
# scientificNameAuthorship
# verbatimEventDate
# sex
# verbatimElevation
# elevationValues
# elevationUnits
# elevationEstimated
# verbatimLatitude
# decimalLatitude
# verbatimLongitude
# decimalLongitude
# recordedBy
# recordNumber
# identifiedBy
# identifiedByID
# occurrenceID
# locality
# country
# stateProvince
# county
# municipality
# waterBody
# island
# islandGroup
# occurrenceRemarks
# habitat

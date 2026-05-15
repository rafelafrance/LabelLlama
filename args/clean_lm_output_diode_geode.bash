#!/bin/bash

uv run llama/clean_llm_output.py \
  --in-file data/diode_geode/rob_gpt_nano_2026-05-14e.csv \
  --out-file data/diode_geode/rob_gpt_nano_2026-05-14e_cleaned.csv


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

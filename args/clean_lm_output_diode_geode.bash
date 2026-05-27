#!/bin/bash

uv run llama/clean_llm_output.py \
  --in-file data/diode_geode/ode_imaging_gpt_nano_2026-05-26a.csv \
  --out-file data/diode_geode/ode_imaging_gpt_nano_2026-05-26a_cleaned.csv \
  --notes "A new batch of diode images to run thru GPT-nano" \
  --column sex \
  --log-file data/diode_geode/ode_imaging_gpt_nano_2026-05-26a_cleaned.log


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

#!/bin/bash

uv run ./llama/compare_output.py \
  --gold data/diode_geode/Abbott_and_Ware_gold.csv \
  --lm data/herbarium/rob_gpt_nano_2026-05-12a_cleaned.csv \
  --out-file data/herbarium/score_dwc_2026-04-28a_gold.html

# scientificName
# scientificNameAuthorship
# suborder
# family
# genus
# subgenus
# specificEpithet
# vernacularName
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

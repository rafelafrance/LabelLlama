#!/bin/bash

uv run llama/postprocess.py \
  --in-file data/diode_geode/label_test_rmnh_nano_2026-05-04a.csv \
  --run-field-models \
  --fields-registry insects \
  --model lm_studio/qwen/qwen3.6-35b-a3b \
  --max-tokens 4096 \
  --context-length 8192 \
  --out-file data/diode_geode/label_test_rmnh_nano_2026-05-04a_post.csv


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

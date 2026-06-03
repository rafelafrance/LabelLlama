#!/bin/bash

uv run llama/clean_llm_output.py \
  --in-file data/diode/gold_std/gold_gpt_nano_2026-06-02a.csv \
  --out-file data/diode/gold_std/gold_gpt_nano_2026-06-02a_clean.csv \
  --prompt prompts/fields/diode.md \
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

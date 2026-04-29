#!/bin/bash

uv run ./llama/gold_std.py \
  --gold-in data/herbarium/gold_std_2026-03-30a_postRPG3_edited.csv \
  --lm-in data/herbarium/gold_std_2026-03-30a_post.csv \
  --out-file data/herbarium/score_dwc_2026-04-28a_gold.html

# source
# text
# extended data
# scientificName
# scientificNameAuthorship
# infraspecificEpithet
# infraspecificNameAuthorship
# family
# associatedTaxa
# verbatimEventDate
# eventDate
# collector
# recordedBy
# collectorNumber
# recordNumber
# identifiedBy
# dateIdentified
# habitat
# occurrenceRemarks
# locality
# country
# stateProvince
# county
# municipality
# geodeticDatum
# trs
# trsTownship
# trsRange
# trsSection
# trsQuad
# utm
# utmNorthing
# utmEasting
# utmZone
# verbatimLatitude
# verbatimLongitude
# verbatimElevation
# elevation
# maxElevation
# elevationUnits
# elevationEstimated
# abundance
# flowersPresent
# flowerColor
# fruitPresent
# fruitColor
# plantHeight
# plantSize
# habit
# leafShape
# leafMargin

#!/bin/bash

uv run ./llama/gold_std.py import-csv \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --gold-csv data/herbarium/CAS_Goldstandard_2026-01-26.csv \
  --file-name "filename" \
  --skip "ElevationUnits" \
  --skip "MaxElevation" \
  --skip "MinElevation" \
  --skip "Who?" \
  --skip "annotation label?" \
  --skip "decimalLatitude" \
  --skip "decimalLongitude" \
  --skip "eventDate" \
  --skip "filename" \
  --skip "minimumElevationInMeters" \
  --skip "verbatimCoordinateSystem" \
  --skip "verbatimCoordinates" \
  --notes "CAS gold standard from Michael"

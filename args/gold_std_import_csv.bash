#!/bin/bash

./llama/gold_std.py import-csv \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --gold-csv data/herbarium/CAS_Goldstandard_2026-01-26.csv \
  --signature cas_v1 \
  --notes 'CAS gold standard from Michael'

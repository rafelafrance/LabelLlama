#!/bin/bash

# cp data/herbarium/labelllama_herbarium_2025-12-11c.duckdb data/herbarium/labelllama_herbarium.duckdb

./llama/extract_dwc.py \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --pre-dwc-run-id 2 \
  --notes 'Verified line joining'

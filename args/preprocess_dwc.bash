#!/bin/bash

./llama/preprocess_dwc.py \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --ocr-run-id 10 \
  --ocr-run-id 12 \
  --limit 100 \
  --notes 'Join lines after removing junk lines'

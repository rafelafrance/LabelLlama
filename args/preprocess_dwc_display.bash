#!/bin/bash

./llama/preprocess_dwc.py \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --display \
  --ocr-run-id 10 \
  --limit 100

#!/bin/bash

./llama/miprov2_optimizer.py \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --optimized-json data/herbarium/miprov2_gemma3_27b_2025-12-17.json \
  --model-name "lm_studio/google/gemma-3-27b" \
  --gold-run-id 1 \
  --limit 10

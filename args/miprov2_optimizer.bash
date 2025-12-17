#!/bin/bash

# ./llama/miprov2_optimizer.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --optimized-json data/herbarium/miprov2_gemma3_27b_2025-12-17.json \
#   --model-name "lm_studio/google/gemma-3-27b" \
#   --context-length 16384 \
#   --gold-run-id 1

./llama/miprov2_optimizer.py \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --optimized-json data/herbarium/miprov2_gemma3_12b_2025-12-17.json \
  --model-name "lm_studio/google/gemma-3-12b" \
  --context-length 16384 \
  --gold-run-id 1

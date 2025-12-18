#!/bin/bash

today=$(date +"%Y-%m-%d")

# ./llama/miprov2_optimizer.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --optimized-json data/herbarium/miprov2_gemma3_27b_"$today"-12-17.json \
#   --model-name "lm_studio/google/gemma-3-27b" \
#   --context-length 16384 \
#   --gold-run-id 1

# ./llama/miprov2_optimizer.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --optimized-json data/herbarium/miprov2_gemma3_12b_"$today".json \
#   --model-name "lm_studio/google/gemma-3-12b" \
#   --context-length 16384 \
#   --gold-run-id 1

./llama/miprov2_optimizer.py \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --optimized-json data/herbarium/miprov2_phi-4_"$today".json \
  --model-name "lm_studio/microsoft/phi-4" \
  --context-length 16384 \
  --gold-run-id 1

# ./llama/miprov2_optimizer.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --optimized-json data/herbarium/miprov2_granite-4_"$today".json \
#   --model-name "lm_studio/unsloth/granite-4.0-h-small-GGUF/granite-4.0-h-small-Q4_K_S.gguf" \
#   --context-length 16384 \
#   --gold-run-id 1

# ./llama/miprov2_optimizer.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --optimized-json data/herbarium/miprov2_llama-3.3_70b_"$today".json \
#   --model-name "lm_studio/meta/llama-3.3-70b" \
#   --context-length 16384 \
#   --gold-run-id 1

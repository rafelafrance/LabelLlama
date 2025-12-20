#!/bin/bash

# cp data/herbarium/labelllama_herbarium_2025-12-11c.duckdb data/herbarium/labelllama_herbarium.duckdb

# ./llama/extract_dwc.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --notes 'Verified line joining' \
#   --ocr-run-id 10 \
#   --temperature 0.1 \
#   --limit 100

# ./llama/extract_dwc.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --model-name "lm_studio/google/gemma-3-12b" \
#   --notes "Try a smaller version of gemma3" \
#   --ocr-run-id 10 \
#   --temperature 0.1 \
#   --limit 100

# ./llama/extract_dwc.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --model-name "lm_studio/microsoft/phi-4" \
#   --notes "Try this popular model" \
#   --ocr-run-id 10 \
#   --temperature 0.1 \
#   --limit 100

# ./llama/extract_dwc.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --model-name "lm_studio/unsloth/granite-4.0-h-small-GGUF/granite-4.0-h-small-Q4_K_S.gguf" \
#   --notes "Try a model with a different architecture" \
#   --ocr-run-id 10 \
#   --temperature 0.1 \
#   --limit 100

# ./llama/extract_dwc.py \
#   --db-path data/herbarium/labelllama_herbarium.duckdb \
#   --model-name "lm_studio/meta/llama-3.3-70b" \
#   --notes "Try a larger model" \
#   --ocr-run-id 10 \
#   --temperature 0.1 \
#   --limit 100

# ./llama/extract_dwc.py \
#    --db-path data/herbarium/labelllama_herbarium.duckdb \
#    --model-name "openai/gpt-5-mini" \
#    --notes "A medium sized ChatGPT test from gold run 1" \
#    --ocr-run-id 10 \
#    --limit 100 \
#    --context-length 65536 \
#    --api-key "$OPENAI_API_KEY"

 ./llama/extract_dwc.py \
    --db-path data/herbarium/labelllama_herbarium.duckdb \
    --model-name "openai/gpt-5-nano" \
    --notes "A small sized ChatGPT test from gold run 1" \
    --ocr-run-id 10 \
    --limit 100 \
    --context-length 65536 \
    --api-key "$OPENAI_API_KEY"

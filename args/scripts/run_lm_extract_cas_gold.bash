#!/bin/bash

uv run llama/run_lm.py \
  --doc-tsv data/herbarium/gold_std_revised_2026-02-24.tsv \
  --lm-tsv data/herbarium/parallel_100_gold_std.tsv \
  --model-name "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --context-length 65536 \
  --threads 100 \
  --no-cache \
  --signature cas_v1

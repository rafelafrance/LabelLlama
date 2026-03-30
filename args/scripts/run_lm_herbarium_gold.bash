#!/bin/bash

uv run llama/run_lm.py \
  --doc-in data/herbarium/gold_docs.tsv \
  --out-file data/herbarium/gold_std_2026-03-30.tsv \
  --model-name "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --context-length 65536 \
  --threads 20 \
  --log-file data/herbarium/history.log \
  --signature herbarium

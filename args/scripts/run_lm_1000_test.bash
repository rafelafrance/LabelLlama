#!/bin/bash

uv run llama/run_lm.py \
  --doc-in data/herbarium/1000_test_docs.csv \
  --out-file data/herbarium/1000_test_2026-04-08.csv \
  --model "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --threads 20 \
  --log-file data/herbarium/1000_test.log \
  --signature herbarium

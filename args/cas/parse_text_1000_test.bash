#!/bin/bash

uv run llama/parse_text.py \
  --docs data/herbarium/1000_test_docs.csv \
  --out-file data/herbarium/1000_test_2026-04-13.csv \
  --model "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --threads 20 \
  --log-file data/herbarium/1000_test.log \
  --signature herbarium

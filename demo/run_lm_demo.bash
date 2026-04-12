#!/bin/bash

uv run llama/run_lm.py \
  --doc-in demo/ocr_demo_docs.csv \
  --out-file demo/lm_extracts.csv \
  --model "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --threads 5 \
  --signature herbarium

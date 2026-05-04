#!/bin/bash

uv run llama/run_llm.py \
  --doc-tsv data/herbarium/gold_docs.tsv \
  --out-file data/herbarium/gold_docs_2026-04-27a.csv \
  --model-name "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --threads 20 \
  --log-file data/herbarium/gold_docs_2026-04-27a.log \
  --signature herbarium

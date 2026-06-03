#!/bin/bash

uv run llama/parse_text.py \
  --docs data/herbarium/gold_docs.tsv \
  --out-file data/herbarium/gold_docs_2026-05-25a.csv \
  --prompt prompts/fields/herbarium.md \
  --model "openai/gpt-5-nano" \
  --threads 20 \
  --notes "Just getting the length of the prompt" \
  --log-file data/herbarium/gold_docs_2026-05-25a.log \

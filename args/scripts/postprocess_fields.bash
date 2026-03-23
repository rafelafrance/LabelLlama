#!/bin/bash

uv run llama/postprocess_fields.py postprocess \
  --db-path data/herbarium/cas_v1.duckdb \
  --results-ods data/herbarium/cleaned_fields_2026-03-22.ods \
  --model-name lm_studio/qwen/qwen3.5-35b-a3b \
  --job-id 14 \
  --db-write \
  --context-length 4096 \
  --notes "Clean fields from the GPT-nano run with expanded fields"

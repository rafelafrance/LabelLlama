#!/bin/bash

uv run llama/postprocess_fields.py postprocess \
  --db-path data/herbarium/cas_v1.duckdb \
  --results-ods data/herbarium/new_gold_2026-03-17.ods \
  --model-name lm_studio/qwen/qwen3.5-35b-a3b \
  --job-id 14 \
  --dry-run \
  --context-length 4096 \
  --field stateProvince \
  --notes "Test postprocessing fields"

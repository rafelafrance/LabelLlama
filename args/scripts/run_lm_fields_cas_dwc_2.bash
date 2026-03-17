#!/bin/bash

uv run llama/run_lm.py fields \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --results-ods data/herbarium/new_dwc_2026-03-05_qwen2.ods \
  --model-name lm_studio/qwen/qwen3-vl-30b \
  --context-length 262144 \
  --dwc-run-id 2 \
  --field locality \
  --notes "Test field extractions"

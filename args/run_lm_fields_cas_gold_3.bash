#!/bin/bash

uv run llama/run_lm.py fields \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --results-ods data/herbarium/new_gold_2026-03-05_qwen2.ods \
  --model-name lm_studio/qwen/qwen3-vl-30b \
  --context-length 262144 \
  --gold-run-id 3 \
  --limit 1 \
  --notes "Test field extractions"

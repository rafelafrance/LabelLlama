#!/bin/bash

uv run llama/run_lm.py fields \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --results-ods data/herbarium/new_gold_2026-03-06_gemma3.ods \
  --model-name lm_studio/google/gemma-3-27b \
  --gold-run-id 3 \
  --notes "Test field extractions"

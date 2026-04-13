#!/bin/bash

uv run llama/postprocess.py \
  --in-file data/herbarium/1000_test_2026-04-13.csv \
  --log-file data/herbarium/1000_test.log \
  --run-field-models \
  --model lm_studio/google/gemma-4-e4b \
  --field occurrenceRemarks \
  --no-cache \
  --out-file data/herbarium/1000_test_2026-04-13a_test.csv

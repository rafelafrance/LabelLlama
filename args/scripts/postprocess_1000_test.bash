#!/bin/bash

uv run llama/postprocess_fields.py \
  --in-file data/herbarium/1000_test_2026-04-08.csv \
  --log-file data/herbarium/1000_test.log \
  --run-field-models \
  --no-cache \
  --limit 100 \
  --field occurrenceRemarks \
  --out-file data/herbarium/1000_tes_2026-04-08b_post.csv

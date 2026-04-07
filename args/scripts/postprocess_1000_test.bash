#!/bin/bash

uv run llama/postprocess_fields.py \
  --in-file data/herbarium/1000_test_2026-04-06.csv \
  --log-file data/herbarium/1000_test.log \
  --run-field-models \
  --no-cache \
  --out-file data/herbarium/1000_tes_2026-04-06b_post.csv

#!/bin/bash

uv run llama/postprocess_fields.py \
  --in-file data/herbarium/gold_std_2026-03-30.tsv \
  --log-file data/herbarium/history.log \
  --run-field-models \
  --no-cache \
  --out-file data/herbarium/gold_std_2026-03-30a_post.csv

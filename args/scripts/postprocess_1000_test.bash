#!/bin/bash

uv run llama/postprocess.py \
  --in-file data/herbarium/1000_test_2026-04-11.csv \
  --log-file data/herbarium/1000_test.log \
  --run-field-models \
  --out-file data/herbarium/1000_test_2026-04-11a_post.csv

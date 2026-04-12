#!/bin/bash

uv run llama/postprocess.py \
  --in-file demo/lm_extracts.csv \
  --run-field-models \
  --out-file demo/lm_extracts_post.csv

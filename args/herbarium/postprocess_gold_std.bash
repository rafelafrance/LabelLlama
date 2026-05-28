#!/bin/bash

uv run llama/postprocess.py \
  --in-file data/herbarium/gold_docs_2026-04-27a.csv \
  --run-field-models \
  --out-file data/herbarium/gold_docs_2026-04-27a_post.csv

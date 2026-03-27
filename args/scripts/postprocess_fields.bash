#!/bin/bash

uv run llama/postprocess_fields.py \
  --in-file data/herbarium/lm_gpt_nano_2026-03-23.tsv \
  --out-file data/herbarium/lm_gpt_nano_2026-03-23_post.tsv

#!/bin/bash

uv run llama/postprocess_fields.py \
  --input-tsv data/herbarium/lm_gpt_nano_2026-03-23.tsv \
  --output-tsv data/herbarium/lm_gpt_nano_2026-03-23a.tsv

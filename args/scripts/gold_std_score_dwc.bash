#!/bin/bash

uv run ./llama/gold_std.py \
  --gold-in data/herbarium/gold_std_revised_2026-02-24.tsv \
  --lm-in data/herbarium/lm_gpt_nano_2026-03-23_post.tsv \
  --out-file data/herbarium/score_dwc_2026-03-27.html

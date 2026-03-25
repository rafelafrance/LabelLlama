#!/bin/bash

uv run ./llama/gold_std.py \
  --gold-tsv data/herbarium/gold_std_revised_2026-02-24.tsv \
  --lm-tsv data/herbarium/lm_gpt_nano_2026-03-23.tsv \
  --output data/herbarium/score_dwc_2026-03-25.tsv

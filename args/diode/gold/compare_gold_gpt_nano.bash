#!/bin/bash

uv run ./llama/compare_output.py \
  --prompt prompts/fields/diode.md \
  --gold-file data/diode/gold_std/Abbott_and_Ware_gold.csv \
  --lm-file data/diode/gold_std/gold_gpt_nano_2026-06-02a_clean.csv \
  --out-file data/diode/gold_std/gold_vs_gpt_nano_2026-06-02a.html

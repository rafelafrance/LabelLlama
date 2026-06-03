#!/bin/bash

uv run ./llama/compare_output.py \
  --prompt prompts/fields/diode.md \
  --gold-file data/diode_geode/diode_imaging_gpt_nano_2026-06-02a_clean.csv \
  --lm-file data/diode_geode/diode_imaging_qwen_2026-06-01a_clean.csv \
  --out-file data/diode_geode/diode_imaging_nano_vs_qwen_2026-06-02.html

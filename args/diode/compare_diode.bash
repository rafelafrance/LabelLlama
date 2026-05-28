#!/bin/bash

uv run ./llama/compare_output.py \
  --prompt prompts/fields/diode.md \
  --gold-file data/diode_geode/ode_imaging_gpt_nano_2026-05-26a_cleaned.csv \
  --lm-file data/diode_geode/ode_imaging_qwen_2026-05-26b_cleaned.csv \
  --out-file data/diode_geode/ode_imaging_nano_vs_qwen.html

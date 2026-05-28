#!/bin/bash

uv run llama/run_lm.py \
  --docs data/diode_geode/diode_imaging_2026-05-26.csv \
  --out-file data/diode_geode/ode_imaging_gpt_nano_2026-05-26a.csv \
  --prompt prompts/fields/diode.md \
  --model "gpt-5-nano-2025-08-07" \
  --threads 20 \
  --notes "Run a new batch of diode images thru GPT-nano" \
  --log-file data/diode_geode/diode_imaging_gpt_nano_2026-05-26a.log

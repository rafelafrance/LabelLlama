#!/bin/bash

uv run llama/parse_text.py \
  --docs data/diode_geode/diode_imaging_2026-05-26.csv \
  --out-file data/diode_geode/diode_imaging_gpt_nano_2026-06-02a.csv \
  --prompt prompts/fields/diode.md \
  --model "gpt-5-nano-2025-08-07" \
  --threads 20 \
  --log-file data/diode_geode/diode_imaging_gpt_nano.log

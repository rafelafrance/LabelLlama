#!/bin/bash

uv run llama/run_lm.py \
  --docs data/diode_geode/rob_odonata_2026-05-11.csv \
  --out-file data/diode_geode/rob_gpt_nano_2026-05-11a.csv \
  --prompt prompts/diode_geode.md \
  --model "gpt-5-nano-2025-08-07" \
  --threads 20 \
  --log-file data/diode_geode/rob_gpt_nano_2026-05-11a.log \
  --signature insect

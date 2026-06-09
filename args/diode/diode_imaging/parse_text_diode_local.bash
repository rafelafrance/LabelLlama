#!/bin/bash

uv run llama/parse_text.py \
  --docs data/diode_geode/diode_imaging_2026-05-26.csv \
  --out-file data/diode_geode/diode_imaging_qwen_2026-06-01a.csv \
  --prompt prompts/fields/diode.md \
  --model "qwen/qwen3.6-35b-a3b" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.0 \
  --threads 4 \
  --log-file data/diode_geode/diode_imaging_qwen.log

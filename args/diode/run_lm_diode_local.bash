#!/bin/bash

uv run llama/run_lm.py \
  --docs data/diode_geode/diode_imaging_2026-05-26.csv \
  --out-file data/diode_geode/diode_imaging_qwen_2026-05-28a.csv \
  --prompt prompts/fields/diode.md \
  --model "qwen/qwen/qwen3.6-35b-a3b" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.1 \
  --threads 4 \
  --notes "Run a new batch of diode images thru a qwen model" \
  --log-file data/diode_geode/diode_imaging_qwen.log

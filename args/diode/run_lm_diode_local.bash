#!/bin/bash

uv run llama/run_lm.py \
  --docs data/diode_geode/ode_imaging_2026-05-26.csv \
  --out-file data/diode_geode/diode_imaging_qwen27_2026-05-27e.csv \
  --prompt prompts/fields/diode.md \
  --model "qwen/qwen3.6-27b" \
  --temperature 0.1 \
  --threads 4 \
  --notes "Run a new batch of diode images thru a qwen model" \
  --limit 10 \
  --api-host http://localhost:1234/v1 \
  --log-file data/diode_geode/diode_imaging_qwen27_2026-05-27e.log

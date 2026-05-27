#!/bin/bash

uv run llama/run_lm.py \
  --docs data/diode_geode/ode_imaging_2026-05-26.csv \
  --out-file data/diode_geode/ode_imaging_qwen_2026-05-26b.csv \
  --prompt prompts/fields/diode_local.md \
  --model "qwen/qwen3.6-35b-a3b" \
  --threads 4 \
  --notes "A new batch of diode images were run thru qwen 3.6" \
  --api-host http://localhost:1234/v1 \
  --log-file data/diode_geode/ode_imaging_qwen_2026-05-26b.log

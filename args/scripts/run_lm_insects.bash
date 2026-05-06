#!/bin/bash

uv run llama/run_llm.py \
  --docs data/diode_geode/label_test_rmnh_2026-05-04.csv \
  --out-file data/diode_geode/label_test_rmnh_nano_2026-05-04a.csv \
  --model "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --threads 20 \
  --log-file data/diode_geode/label_test_rmnh_nano_2026-05-04a.log \
  --signature insect

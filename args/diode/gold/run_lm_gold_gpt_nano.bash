#!/bin/bash

uv run llama/run_lm.py \
  --docs data/diode/gold_std/gold_docs_2026-05-11.csv \
  --out-file data/diode/gold_std/gold_gpt_nano_2026-06-02a.csv \
  --prompt prompts/fields/diode.md \
  --model "gpt-5-nano-2025-08-07" \
  --threads 20 \
  --log-file data/diode/gold_std/gold_std.log

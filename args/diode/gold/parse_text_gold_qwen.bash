#!/bin/bash

uv run llama/parse_text.py \
  --docs data/diode/gold_std/gold_docs_2026-05-11.csv \
  --out-file data/diode/gold_std/gold_qwen_2026-06-02a.csv \
  --prompt prompts/fields/diode.md \
  --model "qwen/qwen/qwen3.6-35b-a3b" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.0 \
  --threads 4 \
  --log-file data/diode/gold_std/gold_std.log

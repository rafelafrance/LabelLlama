#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/herbarium/ufl_images_1.csv \
  --parse-file data/herbarium/ufl_images_1_qwen36_27b_mtp_2026-06-09b.csv \
  --prompt prompts/fields/herbarium.md \
  --model "qwen3.6-27b-mtp" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.1 \
  --max-tokens 4096 \
  --timeout 300 \
  --threads 1 \
  --limit 100 \
  --log-file data/herbarium/ufl_images_qwen.log

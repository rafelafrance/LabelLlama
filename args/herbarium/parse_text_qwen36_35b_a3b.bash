#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/herbarium/ufl_images_1.csv \
  --parse-file data/herbarium/ufl_images_1_qwen36_35b_a3b_2026-06-09a.csv \
  --prompt prompts/fields/herbarium.md \
  --model "qwen/qwen3.6-35b-a3b" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.1 \
  --timeout 120 \
  --threads 4 \
  --log-file data/herbarium/ufl_images_qwen.log

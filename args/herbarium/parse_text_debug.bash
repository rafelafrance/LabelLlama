#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/herbarium/ocr/ocr_ariz_images.csv \
  --parse-file data/herbarium/debug_raw_ariz.csv \
  --prompt prompts/fields/herbarium.md \
  --model "qwen/qwen3.6-35b-a3b" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.1 \
  --timeout 120 \
  --threads 4 \
  --limit 2 \
  --log-file data/herbarium/debug.log

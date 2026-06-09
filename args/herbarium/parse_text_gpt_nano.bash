#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/herbarium/ufl_images_1.csv \
  --parse-file data/herbarium/ufl_images_1_gpt_nano_2026-06-09a.csv \
  --prompt prompts/fields/herbarium.md \
  --model "gpt-5-nano-2025-08-07" \
  --api-host "https://api.openai.com/v1" \
  --threads 20 \
  --log-file data/herbarium/ufl_images_gpt_nano.log

#!/bin/bash

uv run llama/parse_text.py \
  --ocr-file data/herbarium/ufl_images_1.csv \
  --parse-file data/herbarium/ufl_images_1_gemma4_31b_qat_2026-06-14a.csv \
  --prompt prompts/fields/herbarium.md \
  --model "google/gemma4_31b-qat" \
  --api-host "http://localhost:1234/v1" \
  --temperature 0.1 \
  --max-tokens 4096 \
  --timeout 300 \
  --threads 1 \
  --limit 100 \
  --log-file data/herbarium/ufl_images_gemma.log

#!/bin/bash

uv run ./llama/compare_output_gbif.py \
  --prompt prompts/fields/herbarium.md \
  --ocr-file data/herbarium/ocr_ufl_images_1.csv \
  --gbif-file data/herbarium/gbif_ufl_images_1.csv \
  --llm-file data/herbarium/qwen36_35b_a3b_06-09a.csv \
  --llm-file data/herbarium/gpt_nano_06-09a.csv \
  --output-file data/herbarium/compare_ufl_images_1_2026-06-22h.ods \
  --notes "Revised field matching and statistics"

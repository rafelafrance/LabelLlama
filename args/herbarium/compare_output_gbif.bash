#!/bin/bash

uv run ./llama/compare_output_gbif.py \
  --ocr-file data/herbarium/ocr_ufl.csv \
  --gbif-file data/herbarium/gbif_ufl.csv \
  --llm-file data/herbarium/qwen36_35b_a3b_ufl.csv \
  --llm-file data/herbarium/gpt_nano_ufl.csv \
  --limit 2 \
  --output-file data/herbarium/compare_ufl_2026-06-25a.ods

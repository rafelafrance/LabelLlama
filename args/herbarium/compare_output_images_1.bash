#!/bin/bash

uv run ./llama/compare_output_new.py \
  --prompt prompts/fields/herbarium.md \
  --clean-file1 data/herbarium/ufl_images_1_qwen36_35b_a3b_2026-06-09a_clean.csv \
  --clean-file2 data/herbarium/ufl_images_1_gpt_nano_2026-06-09a_clean.csv \
  --compare-file data/herbarium/ufl_images_1_nano_vs_qwen_2026-06-15b.html \
  --gbif-file data/herbarium/ufl_images_1_gbif.csv

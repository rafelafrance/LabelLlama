#!/bin/bash

uv run ./llama/compare_output_gold.py \
  --prompt prompts/fields/herbarium.md \
  --gold-file data/herbarium/ufl_images_1_gbif.csv \
  --clean-file data/herbarium/qwen36_35b_a3b_06-09a.csv \
  --clean-file data/herbarium/gpt_nano_06-09a.csv \
  --html-file data/herbarium/ufl_images_1_compare.html

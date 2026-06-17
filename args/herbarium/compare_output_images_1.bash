#!/bin/bash

uv run ./llama/compare_output_gbif.py \
  --prompt prompts/fields/herbarium.md \
  --gbif-file data/herbarium/ufl_images_1_gbif.csv \
  --llm-file data/herbarium/qwen36_35b_a3b_06-09a.csv \
  --llm-file data/herbarium/gpt_nano_06-09a.csv \
  --html-file data/herbarium/ufl_images_1_compare.html

#!/bin/bash

uv run llama/clean_llm_output.py \
  --parse-file data/herbarium/ufl_images_1_gpt_nano_2026-06-09a.csv \
  --clean-file data/herbarium/ufl_images_1_gpt_nano_2026-06-09a_clean.csv \
  --prompt prompts/fields/herbarium.md \
  --log-file data/herbarium/ufl_images_gpt_nano.log

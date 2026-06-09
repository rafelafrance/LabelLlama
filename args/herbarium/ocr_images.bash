#!/bin/bash

uv run ./llama/ocr_images.py \
  --image-glob 'data/herbarium/ufl_images/*.jpeg' \
  --ocr-file data/herbarium/ufl_images_1.csv \
  --model chandra-ocr \
  --prompt prompts/ocr_v2.md \
  --temperature 0.1 \
  --max-tokens 2048 \
  --log-file data/herbarium/ufl_images.log

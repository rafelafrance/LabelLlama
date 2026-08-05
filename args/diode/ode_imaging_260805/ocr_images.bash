#!/bin/bash

data_dir=data/diode/ode_imaging_260805

uv run ./llama/ocr_images.py \
  --image-glob "$data_dir"/images/"*_card.*" \
  --ocr-file "$data_dir"/ocr_images_260805.csv \
  --prompt prompts/ocr_v2.md \
  --model-name allenai_olmOCR-2-7B-1025-GGUF \
  --temperature 0.1 \
  --max-tokens 2048 \
  --threads 4 \
  --timeout 180 \
  --notes "A new batch of diode images to OCR" \
  --log-file "$data_dir"/ode_imaging.log

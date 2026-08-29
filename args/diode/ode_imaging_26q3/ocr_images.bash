#!/bin/bash

data_dir=data/diode/ode_imaging_260805
uv run ./llama/ocr_images.py \
  --image-glob "$data_dir"/images/"*_card.*" \
  --ocr-file "$data_dir"/ocr_images_260808.csv \
  --prompt prompts/ocr_v2.md \
  --model-id gemma-4-E4B-it-Q8_0 \
  --api-host http://localhost:9931/v1 \
  --temperature 0.1 \
  --max-tokens 2048 \
  --threads 4 \
  --timeout 180 \
  --notes "Try using llama.cpp with a model that works with it." \
  --log-file "$data_dir"/ocr_imaging.log

data_dir=data/diode/fsca
uv run ./llama/ocr_images.py \
  --image-glob "$data_dir"/"images/**/*_card.*" \
  --ocr-file "$data_dir"/ocr_images_260808.csv \
  --prompt prompts/ocr_v2.md \
  --model-id gemma-4-E4B-it-Q8_0 \
  --api-host http://localhost:9931/v1 \
  --temperature 0.1 \
  --max-tokens 2048 \
  --threads 4 \
  --timeout 180 \
  --notes "Try using llama.cpp with a model that works with it." \
  --log-file "$data_dir"/ocr_imaging.log

data_dir=data/diode/amnh
uv run ./llama/ocr_images.py \
  --image-glob "$data_dir"/"images/**/*" \
  --ocr-file "$data_dir"/ocr_images_260809.csv \
  --prompt prompts/ocr_v2.md \
  --model-id gemma-4-E4B-it-Q8_0 \
  --api-host http://localhost:9931/v1 \
  --temperature 0.1 \
  --max-tokens 2048 \
  --threads 4 \
  --timeout 180 \
  --notes "Try using llama.cpp with a model that works with it." \
  --log-file "$data_dir"/ocr_imaging.log

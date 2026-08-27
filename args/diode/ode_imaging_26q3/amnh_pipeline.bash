#!/bin/bash

stamp=$(date +%y%m%d)
data_dir=data/diode/amnh

uv run ./llama/ocr_images.py \
  --image-glob "$data_dir"/"images/DiODE-20260827T160325Z-*/*/**/*" \
  --ocr-file "$data_dir"/ocr_images_"$stamp".csv \
  --prompt prompts/ocr_v2.md \
  --model-id gemma-4-E4B-it-Q8_0 \
  --api-host http://localhost:8080/v1 \
  --temperature 0.1 \
  --max-tokens 2048 \
  --threads 4 \
  --timeout 180 \
  --limit 100 \
  --notes "More AMNH diode images." \
  --log-file "$data_dir"/ocr_imaging.log

# uv run llama/parse_text.py \
#     --ocr-file "$data_dir"/ocr_images_260827.csv \
#     --parsed-file "$data_dir"/parse_text_260827.csv \
#     --prompt prompts/diode_v2.md \
#     --model-id qwen3.6-35b-a3b-mtp \
#     --api-host "http://localhost:1234/v1" \
#     --temperature 0.1 \
#     --timeout 300 \
#     --threads 4 \
#     --notes "More AMNH diode images." \
#     --log-file "$data_dir"/parse_text.log

# uv run llama/clean_text.py \
#     --parsed-file "$data_dir"/parse_text_260827.csv \
#     --clean-file "$data_dir"/clean_text_260827.csv \
#     --prompt prompts/diode_v2.md \
#     --notes "More AMNH diode images." \
#     --log-file "$data_dir"/clean_text.log

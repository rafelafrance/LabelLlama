#!/bin/bash

# Run the 3-step pipeline (OCR -> parse -> clean) in sequence so its output
# can be compared against extract_from_images.bash (the 1-step path).
# Uses the same date stamp and dataset conventions as that script.

set -e

stamp=$(date +%y%m%d)

# data_dir=data/diode/ode_imaging_260805
# uv run ./llama/ocr_images.py \
#   --image-glob "$data_dir"/images/"*_card.*" \
#   --ocr-file "$data_dir"/ocr_images_"$stamp".csv \
#   --prompt prompts/ocr_v2.md \
#   --model-id gemma-4-E4B-it-Q8_0 \
#   --api-host http://localhost:8080/v1 \
#   --temperature 0.1 \
#   --max-tokens 2048 \
#   --threads 4 \
#   --timeout 180 \
#   --log-file "$data_dir"/ocr_imaging.log
#
# uv run llama/parse_text.py \
#     --ocr-file "$data_dir"/ocr_images_"$stamp".csv \
#     --parsed-file "$data_dir"/parse_text_"$stamp".csv \
#     --prompt prompts/diode_v2.md \
#     --model-id qwen3.6-35b-a3b-mtp \
#     --api-host "http://localhost:1234/v1" \
#     --temperature 0.1 \
#     --timeout 300 \
#     --threads 4 \
#     --log-file "$data_dir"/parse_text.log
#
# uv run llama/clean_llm_output.py \
#     --parsed-file "$data_dir"/parse_text_"$stamp".csv \
#     --clean-file "$data_dir"/clean_text_"$stamp".csv \
#     --prompt prompts/diode_v2.md \
#     --log-file "$data_dir"/clean_text.log

data_dir=data/diode/fsca
uv run ./llama/ocr_images.py \
  --image-glob "$data_dir"/"images/**/*_card.*" \
  --ocr-file "$data_dir"/ocr_images_"$stamp".csv \
  --prompt prompts/ocr_v2.md \
  --model-id gemma-4-E4B-it-Q8_0 \
  --api-host http://localhost:8080/v1 \
  --temperature 0.1 \
  --max-tokens 2048 \
  --threads 4 \
  --timeout 180 \
  --notes "3-step pipeline run to compare against extract_from_images.bash." \
  --log-file "$data_dir"/ocr_imaging.log

uv run llama/parse_text.py \
    --ocr-file "$data_dir"/ocr_images_"$stamp".csv \
    --parsed-file "$data_dir"/parse_text_"$stamp".csv \
    --prompt prompts/diode_v2.md \
    --model-id qwen3.6-35b-a3b-mtp \
    --api-host "http://localhost:1234/v1" \
    --temperature 0.1 \
    --timeout 300 \
    --threads 4 \
    --log-file "$data_dir"/parse_text.log

uv run llama/clean_llm_output.py \
    --parsed-file "$data_dir"/parse_text_"$stamp".csv \
    --clean-file "$data_dir"/clean_text_"$stamp".csv \
    --prompt prompts/diode_v2.md \
    --log-file "$data_dir"/clean_text.log

# data_dir=data/diode/amnh
# uv run ./llama/ocr_images.py \
#   --image-glob "$data_dir"/"images/**/*" \
#   --ocr-file "$data_dir"/ocr_images_"$stamp".csv \
#   --prompt prompts/ocr_v2.md \
#   --model-id gemma-4-E4B-it-Q8_0 \
#   --api-host http://localhost:8080/v1 \
#   --temperature 0.1 \
#   --max-tokens 2048 \
#   --threads 4 \
#   --timeout 180 \
#   --log-file "$data_dir"/ocr_imaging.log
#
# uv run llama/parse_text.py \
#     --ocr-file "$data_dir"/ocr_images_"$stamp".csv \
#     --parsed-file "$data_dir"/parse_text_"$stamp".csv \
#     --prompt prompts/diode_v2.md \
#     --model-id qwen3.6-35b-a3b-mtp \
#     --api-host "http://localhost:1234/v1" \
#     --temperature 0.1 \
#     --timeout 300 \
#     --threads 4 \
#     --log-file "$data_dir"/parse_text.log
#
# uv run llama/clean_llm_output.py \
#     --parsed-file "$data_dir"/parse_text_"$stamp".csv \
#     --clean-file "$data_dir"/clean_text_"$stamp".csv \
#     --prompt prompts/diode_v2.md \
#     --log-file "$data_dir"/clean_text.log

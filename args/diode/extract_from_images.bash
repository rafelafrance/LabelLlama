#!/bin/bash

# data_dir=data/diode/ode_imaging_260805
# uv run llama/extract_from_images.py \
#     --image-glob "$data_dir"/images/"*_card.*" \
#     --parsed-file "$data_dir"/extract_from_images_260812.csv \
#     --prompt prompts/diode_one_v1.md \
#     --model-id gpt-nano \
#     --api-host https://api.openai.com/v1 \
#     --temperature 0.1 \
#     --timeout 300 \
#     --threads 20 \
#     --log-file "$data_dir"/extract_from_images.log

data_dir=data/diode/fsca
uv run llama/extract_from_images.py \
    --image-glob "$data_dir"/"images/**/*_card.*" \
    --parsed-file "$data_dir"/extract_from_images_260812.csv \
    --prompt prompts/diode_one_v1.md \
    --model-id gpt-nano \
    --api-host https://api.openai.com/v1 \
    --temperature 0.1 \
    --timeout 300 \
    --threads 20 \
    --log-file "$data_dir"/extract_from_images.log

# data_dir=data/diode/amnh
# uv run llama/extract_from_images.py \
#     --image-glob "$data_dir"/"images/**/*" \
#     --parsed-file "$data_dir"/extract_from_images_260812.csv \
#     --prompt prompts/diode_one_v1.md \
#     --model-id gpt-nano \
#     --api-host https://api.openai.com/v1 \
#     --temperature 0.1 \
#     --timeout 300 \
#     --threads 20 \
#     --log-file "$data_dir"/extract_from_images.log

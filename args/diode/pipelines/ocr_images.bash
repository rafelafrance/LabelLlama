#!/bin/bash

data_dir=data/diode/ode_imaging_260805

export TRITON_DEFAULT_FP_FUSION=1

uv run llama/pipelines/ocr_images.py \
    --image-glob "$data_dir"/images/"*_card.*" \
    --ocr-file "$data_dir"/ocr_images_junk.csv \
    --prompt-md prompts/ocr_v2.md \
    --model-id Qwen/Qwen3.5-4B \
    --max-tokens 2048 \
    --threads 4 \
    --notes "Try OCR with an HF pipeline." \
    --log-file "$data_dir"/junk_imaging.log \
    --limit 1

    # --batch-size 2 \

#!/bin/bash

uv run ./llama/ocr_images.py \
    --image-glob "data/herbarium/images/phenobase_images/*" \
    --ocr-file "data/herbarium/ocr_chandra/ocr_phenobase_images.csv" \
    --model chandra-ocr \
    --prompt prompts/ocr_v2.md \
    --temperature 0.1 \
    --max-tokens 2048 \
    --threads 4 \
    --timeout 300 \
    --log-file data/herbarium/ocr_images.log

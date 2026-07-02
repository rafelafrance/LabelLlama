#!/bin/bash

# for org in "cornell" "harvard" "jepson" "mich" "missouri" "ncu" "wash" "wisc" "wtu"; do
for org in "phenobase"; do
    uv run ./llama/ocr_images.py \
        --image-dir "data/herbarium/images/${org}_images" \
        --ocr-file "data/herbarium/ocr_chandra/ocr_${org}_images.csv" \
        --model chandra-ocr \
        --prompt prompts/ocr_v2.md \
        --temperature 0.1 \
        --max-tokens 2048 \
        --threads 4 \
        --timeout 300 \
        --log-file data/herbarium/ocr_images.log
done

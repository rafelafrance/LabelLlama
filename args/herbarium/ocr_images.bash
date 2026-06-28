#!/bin/bash

# for org in "cornell" "harvard" "jepson" "mich" "missouri" "ncu" "wash" "wisc" "wtu"; do
for org in "cas"; do
    uv run ./llama/ocr_images.py \
        --image-glob "data/herbarium/images/${org}_images/*.jpg" \
        --ocr-file "data/herbarium/ocr_chandra/ocr_${org}_images.csv" \
        --model chandra-ocr \
        --prompt prompts/ocr_v2.md \
        --temperature 0.1 \
        --max-tokens 2048 \
        --threads 4 \
        --timeout 120 \
        --log-file data/herbarium/ocr_images.log
done

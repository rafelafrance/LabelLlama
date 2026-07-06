#!/bin/bash

# for org in "brit" "carnegie" "cornell" "field" "harvard" "nau" "ufl" "wisc" "wsu"; do
for org in "nau"; do
    uv run ./llama/ocr_images.py \
        --image-dir "data/herbarium/images/${org}_images" \
        --ocr-file "data/herbarium/ocr_olmocr2/ocr_${org}_images.csv" \
        --model allenai/olmocr-2-7b \
        --prompt prompts/ocr_v2.md \
        --temperature 0.1 \
        --max-tokens 2048 \
        --threads 4 \
        --timeout 300 \
        --log-file data/herbarium/ocr_olmocr2/ocr_images.log
done

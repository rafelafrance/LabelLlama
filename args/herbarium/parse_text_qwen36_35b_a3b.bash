#!/bin/bash

# for org in "brit" "carnegie" "cas" "cornell" "field" "harvard" "mo" "nau" "ny" "ufl" "wisc" "wsu"; do
for org in "nau"; do
    uv run llama/parse_text.py \
        --ocr-file "data/herbarium/ocr_olmocr2/ocr_${org}_images.csv" \
        --parse-file "data/herbarium/qwen36_35b_a3b_raw/qwen36_35b_a3b_${org}.csv" \
        --prompt prompts/fields/herbarium_v1.md \
        --model "qwen/qwen3.6-35b-a3b" \
        --api-host "http://localhost:1234/v1" \
        --temperature 0.1 \
        --timeout 300 \
        --threads 4 \
        --log-file data/herbarium/qwen36_35b_a3b_raw/parse_text.log
done

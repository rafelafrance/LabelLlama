#!/bin/bash

for org in "nau"; do
    uv run llama/parse_text.py \
        --ocr-file "data/herbarium/ocr_olmocr2/ocr_${org}_images.csv" \
        --parse-file "data/herbarium/gemma4_12b_raw/gemma4_12b_${org}.csv" \
        --prompt prompts/fields/herbarium_v1.md \
        --model "google/gemma-4-12b-qat" \
        --api-host "http://localhost:1234/v1" \
        --temperature 0.1 \
        --timeout 300 \
        --threads 2 \
        --limit 50 \
        --log-file data/herbarium/gemma4_12b_raw/parse_text.log
done

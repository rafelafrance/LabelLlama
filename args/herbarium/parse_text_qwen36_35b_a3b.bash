#!/bin/bash

# for org in "missouri"; do
for org in "ariz" "brit" "cornell" "harvard" "jepson" "mich" "missouri" "ncu" "wash" "wisc" "wtu"; do
    uv run llama/parse_text.py \
        --ocr-file "data/herbarium/ocr_chandra/ocr_${org}_images.csv" \
        --parse-file "data/herbarium/qwen36_35b_a3b_raw/qwen36_35b_a3b_${org}.csv" \
        --prompt prompts/fields/herbarium.md \
        --model "qwen/qwen3.6-35b-a3b" \
        --api-host "http://localhost:1234/v1" \
        --temperature 0.1 \
        --timeout 300 \
        --threads 4 \
        --log-file data/herbarium/parse_text_qwen36_35b_a3b.log
done

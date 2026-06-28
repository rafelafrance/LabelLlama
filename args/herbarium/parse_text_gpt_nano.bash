#!/bin/bash

# for org in "ariz" "brit" "cornell" "harvard" "jepson" "mich" "missouri" "ncu" "wash" "wisc" "wtu"; do
for org in "wisc"; do
    uv run llama/parse_text.py \
        --ocr-file "data/herbarium/ocr_chandra/ocr_${org}_images.csv" \
        --parse-file "data/herbarium/gpt_nano/gpt_nano_${org}.csv" \
        --prompt prompts/fields/herbarium.md \
        --model "gpt-5-nano-2025-08-07" \
        --api-host "https://api.openai.com/v1" \
        --threads 20 \
        --log-file data/herbarium/parse_text_gpt_nano.log
done

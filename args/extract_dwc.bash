#!/bin/bash

./llama/extract_dwc.py \
    --ocr-input data/herbarium/ocr_sheets_001_2025-11-06.jsonl \
    --dwc-output data/herbarium/dwc_sheets_001_2025-11-12.jsonl \
    --max-tokens 8192 \
    --api-base http://localhost:1234/v1 \
    --model-name lm_studio/gemma-3-12b \
    --temperature 0.5 \
    --last 10

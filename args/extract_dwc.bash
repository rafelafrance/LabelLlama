#!/bin/bash

./llama/extract_dwc.py \
    --ocr-input data/herbarium/ocr_sheets_001_2025-11-06.jsonl \
    --dwc-output data/herbarium/dwc_sheets_001_2025-11-12.jsonl \
    --max-tokens 4096 \
    --model-name ollama_chat/gemma3:12b \
    --temperature 0.5 \
    --last 10

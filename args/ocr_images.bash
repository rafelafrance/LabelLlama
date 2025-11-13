#!/bin/bash

./llama/ocr_images.py \
    --image-dir data/herbarium/sheets_001 \
    --ocr-jsonl data/herbarium/ocr_sheets_001_2025-11-06.jsonl \
    --first 234 \
    --last 1000

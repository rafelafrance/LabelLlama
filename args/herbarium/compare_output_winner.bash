#!/bin/bash

uv run ./llama/compare_output_winner.py \
    --ocr-file data/herbarium/ocr_olmocr2/all_ocr_images.csv \
    --parse-file data/herbarium/qwen36_35b_a3b_clean/all_qwen36_35b_a3b_clean.csv \
    --parse-file data/herbarium/gpt_nano_clean/all_gpt_nano_clean.csv \
    --parse-file data/herbarium/gpt_nano_clean/all_gpt_nano_clean.csv \
    --output-file data/herbarium/compare/compare_260707b.ods

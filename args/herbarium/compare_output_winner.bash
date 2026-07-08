#!/bin/bash

uv run ./llama/compare_output_winner.py \
    --ocr-file data/herbarium/ocr_olmocr2/all_ocr_images.csv \
    --parse-file data/herbarium/qwen36_35b_a3b_clean/qwen36_35b_a3b_nau_clean.csv \
    --parse-file data/herbarium/gpt_nano_clean/gpt_nano_nau_clean.csv \
    --parse-file data/herbarium/gemma4_12b_clean/gemma4_12b_nau.csv \
    --output-ods data/herbarium/compare/compare_winner.ods

#!/bin/bash

uv run ./llama/compare_output_gbif.py \
    --ocr-file data/herbarium/ocr_olmocr2/all_ocr_images.csv \
    --gbif-file data/herbarium/gbif_data/all_gbif_data.csv \
    --parse-file data/herbarium/qwen36_35b_a3b_clean/all_qwen36_35b_a3b_clean.csv \
    --parse-file data/herbarium/gpt_nano_clean/all_gpt_nano_clean.csv \
    --output-csv data/herbarium/compare/compare_260710d.ods

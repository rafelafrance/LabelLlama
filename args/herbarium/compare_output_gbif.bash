#!/bin/bash

# for org in "brit" "carnegie" "cas" "cornell" "field" "harvard" "mo" "nau" "ny" "ufl" "wisc" "wsu"; do
#     uv run ./llama/compare_output_gbif.py \
#     --ocr-file data/herbarium/ocr_olmocr2/ocr_"$org"_images.csv \
#     --gbif-file data/herbarium/gbif_data/gbif_"$org".csv \
#     --parse-file data/herbarium/qwen36_35b_a3b_clean/qwen36_35b_a3b_"$org"_clean.csv \
#     --parse-file data/herbarium/gpt_nano_clean/gpt_nano_"$org"_clean.csv \
#     --output-file data/herbarium/compare_test.ods
# done

uv run ./llama/compare_output_gbif.py \
    --ocr-file data/herbarium/ocr_olmocr2/all_ocr_images.csv \
    --gbif-file data/herbarium/gbif_data/all_gbif_data.csv \
    --parse-file data/herbarium/qwen36_35b_a3b_clean/all_qwen36_35b_a3b_clean.csv \
    --parse-file data/herbarium/gpt_nano_clean/all_gpt_nano_clean.csv \
    --output-file data/herbarium/compare/compare_260706b.ods

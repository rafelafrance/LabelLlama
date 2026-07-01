#!/bin/bash

org=ariz

uv run ./llama/compare_output_gbif.py \
  --ocr-file data/herbarium/ocr_chandra/ocr_"$org"_images.csv \
  --gbif-file data/herbarium/gbif_data/gbif_"$org".csv \
  --llm-file data/herbarium/qwen36_35b_a3b_clean/qwen36_35b_a3b_"$org"_clean.csv \
  --llm-file data/herbarium/gpt_nano_clean/gpt_nano_"$org"_clean.csv \
  --output-file data/herbarium/compare_test.ods

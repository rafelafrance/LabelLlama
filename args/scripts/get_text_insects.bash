#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir data/diode_geode/Label\ Test\ RMNH \
  --docs data/diode_geode/label_test_rmnh_2026-05-04.csv \
  --model chandra-ocr \
  --prompt prompts/ocr.md \
  --notes "A new extract with newer code and models" \
  --log-file data/diode_geode/label_test_rmnh_2026-05-04.log

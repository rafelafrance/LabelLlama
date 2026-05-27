#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir data/diode_geode/Ode_Imaging \
  --docs data/diode_geode/ode_imaging_2026-05-26.csv \
  --model chandra-ocr \
  --max-tokens 2048 \
  --prompt prompts/ocr.md \
  --threads 2 \
  --notes "A new batch of diode images to OCR" \
  --glob "*_card" \
  --log-file data/diode_geode/ode_imaging_2026-05-26.log

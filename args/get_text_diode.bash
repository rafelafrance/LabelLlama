#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir data/diode_geode/Rob_Odonata_Images \
  --docs data/diode_geode/rob_odonata_2026-05-11.csv \
  --model chandra-ocr \
  --max-tokens 2048 \
  --prompt prompts/ocr.md \
  --threads 2 \
  --notes "Trying asyncio for OCR" \
  --log-file data/diode_geode/rob_odonata_2026-05-11.log

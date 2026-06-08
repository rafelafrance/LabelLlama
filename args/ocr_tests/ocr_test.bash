#!/bin/bash

uv run ./llama/ocr_images.py \
  --image-dir data/mix/ocr_test \
  --docs data/mix/chandra_docs_3.csv \
  --model chandra-ocr \
  --prompt prompts/ocr_v2.md \
  --limit 10 \
  --temperature 0.1 \
  --max-tokens 2048 \
  --log-file data/mix/chandra_ocr.log

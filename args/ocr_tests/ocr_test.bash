#!/bin/bash

uv run ./llama/ocr_images.py \
  --image-dir data/mix/ocr_test \
  --docs data/mix/qwen36_docs_1.csv \
  --model qwen/qwen3.6-35b-a3b \
  --prompt prompts/ocr.md \
  --limit 10 \
  --temperature 0.1 \
  --log-file data/mix/qwen_ocr.log

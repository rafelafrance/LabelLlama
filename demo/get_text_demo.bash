#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir demo/images \
  --docs demo/ocr_demo_docs.csv \
  --model chandra-ocr

#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir demo/images \
  --doc-csv demo/ocr_demo_docs.csv \
  --model chandra-ocr

#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir data/herbarium/1000_test/images \
  --doc-csv data/herbarium/bug.csv \
  --limit 10 \
  --model chandra-ocr

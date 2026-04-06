#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir data/herbarium/1000_test/images \
  --doc-csv data/herbarium/1000_test.csv \
  --model allenai/olmocr-2-7b \
  --log-file data/herbarium/1000_test.log

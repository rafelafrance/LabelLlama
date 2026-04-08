#!/bin/bash

uv run ./llama/get_text.py \
  --image-dir data/herbarium/1000_test/images \
  --doc-csv data/herbarium/1000_test_docs.csv \
  --model chandra-ocr \
  --log-file data/herbarium/1000_test.log

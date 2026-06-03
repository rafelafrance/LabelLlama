#!/bin/bash

uv run ./llama/ocr_images.py \
  --image-dir data/herbarium/1000_test/images \
  --docs data/herbarium/1000_test_docs.csv \
  --model chandra-ocr \
  --prompt prompts/ocr.md \
  --log-file data/herbarium/1000_test.log

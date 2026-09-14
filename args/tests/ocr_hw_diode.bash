#!/bin/bash

data_dir=data/hw/diode
uv run ./llama/ocr_images.py \
  --image-glob "$data_dir"/"**/*" \
  --ocr-file "$data_dir"/chandra-ocr-2-GGUF:Q8_0.csv \
  --model-id prithivMLmods/chandra-ocr-2-GGUF:Q8_0 \
  --prompt-md prompts/ocr_v2.md \
  --api-host http://localhost:9931/v1 \
  --convert-html \
  --max-tokens 2048 \
  --threads 4 \
  --timeout 180 \
  --log-file "$data_dir"/hw_ocr.log

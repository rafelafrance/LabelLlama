#!/bin/bash

./llama/run_lm.py \
  --label-type bug \
  --label-json ./data/diode/olmocr_text_2.json \
  --annotations-json ./data/diode/gpt5_mini_annotations_3.json \
  --model openai/gpt-5-mini \
  --temperature 1.0 \
  --max-tokens 16000 \
  --api-key "$OPENAI_API_KEY"

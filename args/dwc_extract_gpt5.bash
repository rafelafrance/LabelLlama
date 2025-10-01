#!/bin/bash

./llama/run_lm.py \
    --label-type bug \
    --label-json ./data/diode/trial_run_ocr_text.json \
    --annotations-json ./data/diode/gpt5_annotations.json \
    --model openai/gpt-5 \
    --temperature 1.0 \
    --max-tokens 16000 \
    --api-key "$OPENAI_API_KEY"

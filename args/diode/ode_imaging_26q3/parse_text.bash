#!/bin/bash

uv run llama/parse_text.py \
    --ocr-file data/diode/ode_imaging_260805/ocr_images_260808.csv \
    --parse-file data/diode/ode_imaging_260805/parse_text_260810g.csv \
    --prompt prompts/diode_v2.md \
    --model google/gemma-4-26b-a4b \
    --api-host "http://localhost:1234/v1" \
    --temperature 0.1 \
    --timeout 300 \
    --threads 4 \
    --log-file data/diode/ode_imaging_260805/parse_text.log

    # --model qwen3.6-35b-a3b-mtp \

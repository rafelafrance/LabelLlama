#!/bin/bash

data_dir=data/diode/ode_imaging_260805
uv run llama/parse_text.py \
    --ocr-file "$data_dir"/ocr_images_260808.csv \
    --parse-file "$data_dir"/parse_text_260810.csv \
    --prompt prompts/diode_v2.md \
    --model qwen3.6-35b-a3b-mtp \
    --api-host "http://localhost:1234/v1" \
    --temperature 0.1 \
    --timeout 300 \
    --threads 4 \
    --log-file "$data_dir"/parse_text.log

data_dir=data/diode/fsca
uv run llama/parse_text.py \
    --ocr-file "$data_dir"/ocr_images_260808.csv \
    --parse-file "$data_dir"/parse_text_260810.csv \
    --prompt prompts/diode_v2.md \
    --model qwen3.6-35b-a3b-mtp \
    --api-host "http://localhost:1234/v1" \
    --temperature 0.1 \
    --timeout 300 \
    --threads 4 \
    --log-file "$data_dir"/parse_text.log

data_dir=data/diode/amnh
uv run llama/parse_text.py \
    --ocr-file "$data_dir"/ocr_images_260809.csv \
    --parse-file "$data_dir"/parse_text_260810.csv \
    --prompt prompts/diode_v2.md \
    --model qwen3.6-35b-a3b-mtp \
    --api-host "http://localhost:1234/v1" \
    --temperature 0.1 \
    --timeout 300 \
    --threads 4 \
    --log-file "$data_dir"/parse_text.log

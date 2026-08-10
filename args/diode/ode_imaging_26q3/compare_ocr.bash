#!/bin/bash

uv run llama/compare_ocr.py \
    --ocr-file data/diode/ode_imaging_260805/ocr_images_260805.csv \
    --ocr-file data/diode/ode_imaging_260805/ocr_images_260808.csv

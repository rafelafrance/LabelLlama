#!/bin/bash

# for org in "brit" "carnegie" "cornell" "field" "harvard" "nau" "ufl" "wisc" "wsu"; do
for org in "brit"; do
    uv run ./llama/extract_info_one_model.py \
        --image-dir "data/herbarium/images/${org}_images" \
        --extractions "data/herbarium/extractions/extractions_${org}.csv" \
        --api-host http://localhost:8080/v1 \
        --prompt prompts/herbarium_v2.md \
        --model Qwen3.6-35B-A3B-UD-Q6_K_XL \
        --timeout 300 \
        --threads 4 \
        --log-file data/herbarium/extractions/extractions.log
done

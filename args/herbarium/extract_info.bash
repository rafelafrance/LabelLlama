#!/bin/bash

# for org in "brit" "carnegie" "cornell" "field" "harvard" "nau" "ufl" "wisc" "wsu"; do
for org in "brit"; do
    uv run ./llama/extract_info.py \
        --image-dir "data/herbarium/images/${org}_images" \
        --extractions "data/herbarium/extractions/extractions_${org}.csv" \
        --prompt prompts/herbarium_v1.md \
        --timeout 300 \
        --threads 2 \
        --log-file data/herbarium/extractions/extractions.log
done

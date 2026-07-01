#!/bin/bash

# for org in "brit" "carnegie" "cornell" "field" "harvard" "mo" "nau" "nybg" "wisc" "wsu"; do
for org in "brit"; do
    uv run ./llama/util_image_download.py \
        --multimedia-tsv "data/herbarium/downloads/${org}/multimedia.txt" \
        --image-dir "data/herbarium/images/${org}_images" \
        --limit 10 \
        --log-file data/herbarium/util_image_download.log
done

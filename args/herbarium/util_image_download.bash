#!/bin/bash

for org in "brit" "carnegie" "cornell" "field" "harvard" "nau" "wisc" "wsu"; do
    uv run ./llama/util_get_gbif_data.py \
        --multimedia-tsv "data/herbarium/downloads/${org}/multimedia.txt" \
        --image-dir "data/herbarium/images/${org}_images" \
        --limit 50 \
        --offset 1000 \
        --log-file data/herbarium/util_image_download.log
done

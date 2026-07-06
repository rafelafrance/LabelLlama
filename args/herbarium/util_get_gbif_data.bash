#!/bin/bash

for org in "brit" "carnegie" "cornell" "field" "harvard" "nau" "wisc" "wsu"; do
    uv run ./llama/util_get_gbif_data.py \
        --image-dir "data/herbarium/images/${org}_images" \
        --occurrence-tsv "data/herbarium/downloads/${org}/occurrence.txt" \
        --multimedia-tsv "data/herbarium/downloads/${org}/multimedia.txt" \
        --gbif-file "data/herbarium/gbif_data/gbif_${org}.csv"
done

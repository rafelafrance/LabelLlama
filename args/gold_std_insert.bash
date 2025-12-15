#!/bin/bash

./llama/gold_std.py \
  --action insert \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --gold-json data/herbarium/gold_std_2025-12-14.json \
  --notes 'A first try at a gold standard'

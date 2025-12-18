#!/bin/bash

./llama/gold_std.py split \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --gold-run-id 1

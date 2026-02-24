#!/bin/bash

uv run ./llama/gold_std.py score-dwc \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --pause \
  --dwc-run-id 2 \
  --gold-run-id 2

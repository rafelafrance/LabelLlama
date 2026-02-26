#!/bin/bash

uv run ./llama/gold_std.py score-dwc \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --dwc-run-id 2 \
  --gold-run-id 3 \
  --results-ods data/herbarium/score_dwc_2026-02-26.ods

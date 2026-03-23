#!/bin/bash

uv run ./llama/gold_std.py score \
  --db-path data/herbarium/cas_v1.duckdb \
  --gold-job-id 17 \
  --lm-job-id 19 \
  --output data/herbarium/score_dwc_2026-03-23.ods

#!/bin/bash

uv run llama/run_lm.py fields \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --dwc-run-id 2 \
  --notes "Test field extractions "

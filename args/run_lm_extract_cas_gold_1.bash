#!/bin/bash

uv run llama/run_lm.py extract \
  --db-path data/herbarium/labelllama_herbarium.duckdb \
  --signature herbarium \
  --gold-run-id 2 \
  --model-name "openai/gpt-5-nano" \
  --api-key "$OPENAI_API_KEY" \
  --context-length 65536 \
  --signature cas_v1 \
  --notes "Test baseline extraction for 100 CAS gold records -- Modified prompt"

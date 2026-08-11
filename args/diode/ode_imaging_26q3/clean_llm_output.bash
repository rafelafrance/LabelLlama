#!/bin/bash

# data_dir=data/diode/ode_imaging_260805
# uv run llama/clean_llm_output.py \
#     --parsed-file "$data_dir"/parse_text_260809.csv \
#     --clean-file "$data_dir"/clean_text_260811.csv \
#     --prompt prompts/diode_v2.md \
#     --log-file "$data_dir"/parse_text.log

# data_dir=data/diode/fsca
# uv run llama/clean_llm_output.py \
#     --parsed-file "$data_dir"/parse_text_260810.csv \
#     --clean-file "$data_dir"/clean_text_260811.csv \
#     --prompt prompts/diode_v2.md \
#     --log-file "$data_dir"/parse_text.log

data_dir=data/diode/amnh
uv run llama/clean_llm_output.py \
    --parsed-file "$data_dir"/parse_text_260810.csv \
    --clean-file "$data_dir"/clean_text_260811.csv \
    --prompt prompts/diode_v2.md \
    --log-file "$data_dir"/parse_text.log

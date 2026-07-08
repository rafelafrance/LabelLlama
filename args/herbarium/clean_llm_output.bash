#!/bin/bash

# #####################################################################################
clean_dir=data/herbarium/gpt_nano_clean
mkdir -p "$clean_dir"

for parse_file in data/herbarium/gpt_nano_raw/*.csv; do
    name=$(basename "$parse_file" .csv)
    uv run llama/clean_llm_output.py \
        --parse-file "$parse_file" \
        --clean-file "$clean_dir"/"$name"_clean.csv \
        --prompt prompts/fields/herbarium.md \
        --log-file data/herbarium/gpt_nano_clean/clean.log
done

# #####################################################################################
clean_dir=data/herbarium/qwen36_35b_a3b_clean
mkdir -p "$clean_dir"

for parse_file in data/herbarium/qwen36_35b_a3b_raw/*.csv; do
    name=$(basename "$parse_file" .csv)
    uv run llama/clean_llm_output.py \
        --parse-file "$parse_file" \
        --clean-file "$clean_dir"/"$name"_clean.csv \
        --prompt prompts/fields/herbarium.md \
        --log-file data/herbarium/qwen36_35b_a3b_clean/clean.log
done
# #####################################################################################
clean_dir=data/herbarium/gemma4_12b_clean
mkdir -p "$clean_dir"

for parse_file in data/herbarium/gemma4_12b_raw/*.csv; do
    name=$(basename "$parse_file" .csv)
    uv run llama/clean_llm_output.py \
        --parse-file "$parse_file" \
        --clean-file "$clean_dir"/"$name"_clean.csv \
        --prompt prompts/fields/herbarium.md \
        --log-file data/herbarium/gemma4_12b_clean/clean.log
done

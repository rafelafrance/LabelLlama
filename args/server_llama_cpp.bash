#!/bin/bash

~/llm/llama.cpp/build/bin/llama-server \
    --model ~/llm/models/unsloth/Qwen3.6-35B-A3B-UD-Q6_K_XL/Qwen3.6-35B-A3B-UD-Q6_K_XL.gguf \
    --mmproj ~/llm/models/unsloth/Qwen3.6-35B-A3B-UD-Q6_K_XL/mmproj-F32.gguf \
    --reasoning off \
    --gpu-layers all \
    --threads-http 4 \
    --spec-type draft-mtp \
    --spec-draft-n-max 2

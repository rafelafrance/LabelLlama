#!/bin/bash

~/llm/llama.cpp/build/bin/llama-server \
    --model ~/llm/models/Qwen3.6-35B-A3B-UD-Q6_K_XL.gguf \
    --mmproj ~/llm/models/mmproj-F32_qwen36_35b.gguf \
    --reasoning off \
    --gpu-layers all \
    --threads-http 4 \
    --spec-type draft-mtp \
    --spec-draft-n-max 2

# --model ~/llm/models/Qwen3.6-35B-A3B-UD-Q6_K_XL.gguf \
# --mmproj ~/llm/models/mmproj-F32_qwen36_35b.gguf \
# --model ~/llm/models/Qwen3.6-27B-UD-Q8_K_XL.gguf \
# --mmproj ~/llm/models/mmproj-F32_qwen36_27b.gguf \
# --spec-type draft-mtp \
# --spec-draft-n-max 2

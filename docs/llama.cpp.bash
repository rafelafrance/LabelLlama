# llama.cpp/docs/build for HIP/ROCm

HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DCMAKE_BUILD_TYPE=Release &&
  cmake --build build --config Release -- -j 16

# Unified memory
# export GML_CUDA_ENABLE_UNIFIED_MEMORY=1  # Slows things down if you don't use unified memory

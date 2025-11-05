# llama.cpp/docs/build for HIP/ROCm

HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
  cmake -S . -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DCMAKE_BUILD_TYPE=Release &&
  cmake --build build --config Release -- -j 16

# Unified memory
# export GML_CUDA_ENABLE_UNIFIED_MEMORY=1  # Slows things down if you don't use unified memory and you do this

# ************************************************************************************
# pytorch & ROCm

# I needed to install the nightly for ROCm v7.0 and set the following environment variable
export TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1

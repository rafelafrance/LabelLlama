import gc
import subprocess
from typing import Any

import torch


def release_gpu_memory_hf(model: Any) -> None:
    """
    Release GPU memory.

    Models will hold onto the memory for a while if not forced to release it.
    There has to be a better way.
    """
    model.to("cpu")
    del model
    torch.cuda.empty_cache()
    gc.collect()


def release_gpu_memory_ollama(model: str) -> None:
    """
    Release GPU memory.

    Models will hold onto the memory for a while if not forced to release it.
    Again, there has to be a better way.
    """
    model = model.split("/")[-1]
    subprocess.run(["ollama", "stop", model], check=False, shell=True)

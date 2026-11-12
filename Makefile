.PHONY: test clean nvidia rocm hipergator hipergator_once
.ONESHELL:

test:
	uv run -m unittest discover

nvidia:
	uv venv
	source .venv/bin/activate
	uv sync
	uv add torch torchvision
	uv add transformers
	uv add accelerate
	uv add flash-linear-attention
	uv add causal-conv1d

rocm:
	uv venv
	source .venv/bin/activate
	uv sync
	uv pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm7.14
	uv pip install transformers
	uv pip install accelerate
	uv pip install flash-linear-attention
	export CAUSAL_CONV1D_SKIP_CUDA_BUILD=TRUE
	uv pip install causal-conv1d

hipergator:
	uv venv
	source .venv/bin/activate
	uv add torch torchvision transformers accelerate flash-linear-attention causal-conv1d

hipergator_once:
	mv ~/.cache /blue/guralnick/rafe.lafrance/.cache
	ln -s /blue/guralnick/rafe.lafrance/.cache ~/.cache

clean:
	rm -rf .venv
	rm -rf build
	find -iname "*.pyc" -delete

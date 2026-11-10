.PHONY: test clean
.ONESHELL:

test:
	uv run -m unittest discover

rocm:
	uv venv
	source .venv/bin/activate
	uv sync
	uv pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm7.14
	uv pip install transformers
	uv pip install accelerate
	uv pip install flash-linear-attention
	uv pip install causal-conv1d

clean:
	rm -rf .venv
	rm -rf build
	find -iname "*.pyc" -delete

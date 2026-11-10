.PHONY: test clean
.ONESHELL:

test:
	uv run -m unittest discover

dev:
	uv venv && source .venv/bin/activeate
	uv sync
	uv pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm7.14
	uv pip install transformers
	uv pip install accelerate
	uv pip install flash-linear-attention
	uv pip install casual-conv1d

clean:
	rm -rf .venv
	rm -rf build
	find -iname "*.pyc" -delete

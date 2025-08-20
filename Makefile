.PHONY: test install dev clean
.ONESHELL:

test:
	uv run -m unittest discover

install:
	uv sync

dev:
	uv sync

clean:
	rm -rf .venv
	rm -rf build
	rm -rf LabelLlama.egg-info
	find -iname "*.pyc" -delete

.PHONY: test clean install
.ONESHELL:

test:
	uv run -m unittest discover

spacy:
	uv run -- spacy download en_core_web_md

clean:
	rm -rf .venv
	rm -rf build
	find -iname "*.pyc" -delete

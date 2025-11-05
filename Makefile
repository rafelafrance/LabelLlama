.PHONY: test clean
.ONESHELL:

test:
	uv run -m unittest discover

clean:
	rm -rf .venv
	rm -rf build
	find -iname "*.pyc" -delete

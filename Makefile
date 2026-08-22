.PHONY: test clean
.ONESHELL:

test:
	uv run pytest -q

clean:
	rm -rf .venv
	rm -rf build
	find -iname "*.pyc" -delete

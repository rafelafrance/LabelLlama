.PHONY: test install dev clean
.ONESHELL:

test:
	python3.12 -m unittest discover

install:
	test -d .venv || python3.12 -m venv .venv
	. .venv/bin/activate
	python3.12 -m pip install -U pip setuptools wheel
	python3.12 -m pip install .

dev:
	test -d .venv || python3.12 -m venv .venv
	. .venv/bin/activate
	python3.12 -m pip install -U pip setuptools setuptools-scm wheel
	python3.12 -m pip install -e .[dev]
	pre-commit install

clean:
	rm -rf .venv
	find -iname "*.pyc" -delete

install:
	pip install -r requirements.txt pytest

test:
	python -m pytest -q tests

.PHONY: install test

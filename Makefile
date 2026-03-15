PYTHON ?= python3

.PHONY: test lint format

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m flake8 src tests main.py

format:
	$(PYTHON) -m black src tests main.py

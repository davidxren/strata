PYTHON ?= python3.12
VENV := .venv
PY := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,$(PYTHON))

.PHONY: setup test lint fmt bench

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install -e ".[dev]"

test:
	$(PY) -m pytest --continue-on-collection-errors

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .
	$(PY) -m mypy

fmt:
	$(PY) -m ruff check --fix .
	$(PY) -m ruff format .

bench:
	$(PY) -m strata.cli bench

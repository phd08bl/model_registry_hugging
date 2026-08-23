# Optional POSIX/Make convenience targets. Use README PowerShell commands on Windows.
.PHONY: install run test lint format-check compile quality demo-mock

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

demo-mock:
	LLM_MODE=mock uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

test:
	python -m pytest

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

compile:
	python -m compileall -q app tests

quality: test lint format-check compile

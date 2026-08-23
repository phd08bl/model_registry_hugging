.PHONY: install run test lint demo-mock

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

demo-mock:
	LLM_MODE=mock uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

test:
	pytest

lint:
	ruff check app tests


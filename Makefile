.PHONY: lint test eval format

lint:
	ruff check .

test:
	pytest

eval:
	pytest

format:
	ruff format .

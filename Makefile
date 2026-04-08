.PHONY: install train serve test lint data

install:
	pip install -e ".[dev]"

train:
	python -m src.models.train

serve:
	uvicorn src.serving.app:app --reload

test:
	pytest tests/ --cov=src

lint:
	ruff check src/ tests/ evaluation/
	mypy src/ --ignore-missing-imports
	bandit -r src/ -c pyproject.toml

data:
	mkdir -p data/raw data/processed data/golden_set

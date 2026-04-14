.PHONY: install train serve test lint data pipeline eval

eval:
	@echo "🧪 Running DVC evaluation..."
	ambi/bin/dvc repro evaluate


PYTHON = ambi/bin/python

install:
	$(PYTHON) -m pip install -e ".[dev]"

train:
	python -m src.models.train

serve:
	PYTHONPATH=. $(PYTHON) app/app.py

test:
	pytest tests/ --ignore=tests/test_guardrails_unit.py --cov=src

lint:
	ambi/bin/ruff check .
	ambi/bin/mypy . --ignore-missing-imports
	ambi/bin/bandit -r src/ -c pyproject.toml

data:
	mkdir -p data/raw data/processed data/golden_set

pipeline:
	@echo "🔄 Running DVC pipeline..."
	ambi/bin/dvc repro inference
	@echo "✅ Pipeline ML concluído!"

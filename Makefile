.PHONY: install train serve test lint data pipeline eval drift

# Caminhos dos binários (vazio por padrão para usar o PATH do sistema)
BIN_DIR ?= 
PYTHON  ?= $(BIN_DIR)python
DVC     ?= $(BIN_DIR)dvc
RUFF    ?= $(BIN_DIR)ruff
MYPY    ?= $(BIN_DIR)mypy
BANDIT  ?= $(BIN_DIR)bandit

eval:
	@echo "🧪 Running DVC evaluation..."
	$(DVC) repro evaluate

drift:
	@echo "📊 Running Data Drift Analysis..."
	$(DVC) repro drift

install:
	$(PYTHON) -m pip install -e ".[dev]"

train:
	$(PYTHON) -m src.models.train

serve:
	PYTHONPATH=. $(PYTHON) app/app.py

test:
	$(PYTHON) -m pytest tests/ --ignore=tests/test_guardrails_unit.py --cov=src

lint:
	$(RUFF) check .
	$(MYPY) . --ignore-missing-imports
	$(BANDIT) -r src/ -c pyproject.toml

data:
	mkdir -p data/raw data/processed data/golden_set

pipeline:
	@echo "🔄 Running DVC complete pipeline (Train + Inference + Drift)..."
	$(DVC) repro drift
	@echo "✅ Pipeline ML Completo e Relatório de Drift Gerado!"

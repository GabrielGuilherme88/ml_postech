.PHONY: install train serve test lint data pipeline

PYTHON = ambi/bin/python

install:
	$(PYTHON) -m pip install -e ".[dev]"

train:
	python -m src.models.train

serve:
	PYTHONPATH=. $(PYTHON) app/app.py

test:
	pytest tests/ --cov=src

lint:
	ruff check src/ tests/ evaluation/
	mypy src/ --ignore-missing-imports
	bandit -r src/ -c pyproject.toml

data:
	mkdir -p data/raw data/processed data/golden_set

pipeline:
	@echo "🔄 Inicializando banco e resetando a tabela..."
	$(PYTHON) db_lite/create_db.py
	@echo "📊 Abastecendo base com 100 dados simulados..."
	$(PYTHON) db_lite/data_base.py
	@echo "🤖 Treinando modelo Random Forest..."
	$(PYTHON) src/models/train.py
	@echo "🔮 Prevendo 'EM ANALISE' e exportando para db_model..."
	$(PYTHON) src/models/insert_db_model.py
	@echo "✅ Pipeline ML concluido!"

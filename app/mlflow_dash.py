import os
from pathlib import Path
from a2wsgi import WSGIMiddleware
from mlflow.server import app as mlflow_flask_app

# ---------------------------------------------------------------------------
# Configuração do MLflow
# ---------------------------------------------------------------------------

# Caminho para o banco de dados unificado
DB_PATH = Path(__file__).resolve().parents[1] / "db_lite" / "mlflow.db"
TRACKING_URI = f"sqlite:///{DB_PATH}"

# Define a variável de ambiente APENAS se não houver uma Tracking URI externa (como o container mlflow)
if not os.getenv("MLFLOW_TRACKING_URI"):
    os.environ["MLFLOW_TRACKING_URI"] = TRACKING_URI

# Envelopa o app Flask do MLflow para compatibilidade com ASGI (FastAPI)
mlflow_app = WSGIMiddleware(mlflow_flask_app)

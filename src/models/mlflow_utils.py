import os
import mlflow
import mlflow.sklearn
from pathlib import Path
from dotenv import load_dotenv

def setup_mlflow():
    """Configura a URI de tracking do MLflow a partir do ambiente ou fallback para SQLite."""
    load_dotenv()
    
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
        print(f"📡 MLflow Tracking URI definida para: {tracking_uri}")
    else:
        caminho_base = Path(__file__).resolve().parents[2]
        db_path = caminho_base / "db_lite" / "meu_banco_de_dados.db"
        mlflow.set_tracking_uri(f"sqlite:///{db_path}")
        print(f"📁 MLflow Tracking URI usando fallback SQLite: {db_path}")

    mlflow.set_experiment("Previsor_de_Glosas")

from mlflow.models.signature import infer_signature

def log_training(modelo, parametros, metricas, X_train, nome_run="RandomForest_Glosas_v1"):
    """
    Registra os dados do treinamento no MLflow.
    """
    with mlflow.start_run(run_name=nome_run) as run:
        # Log de parâmetros
        mlflow.log_params(parametros)
        
        # Log de métricas
        for nome_metrica, valor in metricas.items():
            mlflow.log_metric(nome_metrica, valor)
        
        # Inferindo assinatura do modelo
        signature = infer_signature(X_train, modelo.predict(X_train))
        
        # Log do modelo com assinatura e exemplo
        mlflow.sklearn.log_model(
            sk_model=modelo,
            artifact_path="modelo_glosa",
            signature=signature,
            input_example=X_train.iloc[:5]
        )
        
        # Log de tags úteis
        mlflow.set_tag("model_type", "RandomForest")
        mlflow.set_tag("version", "0.1.0")

        print(f"🔗 MLflow Run ID salvo: {run.info.run_id}")
        return run.info.run_id

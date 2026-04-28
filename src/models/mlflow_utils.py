import os
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from pathlib import Path
from dotenv import load_dotenv
import time

def setup_mlflow(experiment_name="Previsor_de_Glosas"):
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

    # Retry para aguardar MLflow estar pronto
    for i in range(10):
        try:
            mlflow.set_experiment(experiment_name)
            print("✅ Conectado ao MLflow com sucesso!")
            return
        except Exception as e:
            print(f"⏳ Aguardando MLflow... tentativa {i+1}/10: {e}")
            time.sleep(5)
    
    raise RuntimeError("❌ Não foi possível conectar ao MLflow após 10 tentativas")


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

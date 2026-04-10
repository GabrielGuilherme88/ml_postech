import mlflow
import mlflow.sklearn
from pathlib import Path

def setup_mlflow():
    """Configura a URI de tracking e o experimento do MLflow no banco de dados unificado."""
    caminho_base = Path(__file__).resolve().parents[2]
    # Apontando para o banco de dados principal
    db_path = caminho_base / "db_lite" / "meu_banco_de_dados.db"
    mlflow.set_tracking_uri(f"sqlite:///{db_path}")
    mlflow.set_experiment("Previsor_de_Glosas")

def log_training(modelo, parametros, metricas, nome_run="RandomForest_Glosas_v1"):
    """
    Registra os dados do treinamento no MLflow.
    
    Args:
        modelo: O modelo treinado.
        parametros (dict): Dicionário com os hiperparâmetros.
        metricas (dict): Dicionário com as métricas de performance.
        nome_run (str): Nome identificador da execução.
    """
    with mlflow.start_run(run_name=nome_run) as run:
        # Log de parâmetros
        mlflow.log_params(parametros)
        
        # Log de métricas
        for nome_metrica, valor in metricas.items():
            mlflow.log_metric(nome_metrica, valor)
        
        # Log do modelo
        mlflow.sklearn.log_model(modelo, "modelo_glosa")
        
        print(f"🔗 MLflow Run ID salvo: {run.info.run_id}")
        return run.info.run_id

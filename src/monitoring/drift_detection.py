import os
import sqlite3
import pandas as pd
from pathlib import Path
import sys

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset



import mlflow
from src.models.mlflow_utils import setup_mlflow

def run_drift_detection():
    # Caminho base do projeto
    base_dir = Path(__file__).resolve().parents[2]
    sys.path.append(str(base_dir))
    
    # Caminho do banco de dados (onde estão os pedidos originais e as inferências do modelo)
    db_path = os.getenv("DATABASE_PATH", str(base_dir / "db_lite" / "meu_banco_de_dados.db"))
    output_path = os.getenv("EVIDENTLY_OUTPUT", str(base_dir / "reports" / "drift_report.html"))

    if not os.path.exists(db_path):
        print(f"Banco de dados não encontrado: {db_path}")
        return

    print(f"Conectando ao banco de dados: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # Referência: Todo o dataset histórico ('PAGO' ou 'INDEFERIDO') que foi usado base no modelo
    reference_df = pd.read_sql("SELECT * FROM pedidos_reembolso WHERE nm_situacaoreembolso != 'EM ANALISE'", conn)
    conn.close()
    
    # Produção (Current): Dados inferidos pelo modelo e salvos na tabela db_model
    db_model_path = os.getenv("DATABASE_MODEL_PATH", str(base_dir / "db_lite" / "meu_banco_de_dados.db"))
    
    try:
        conn_model = sqlite3.connect(db_model_path)
        current_df = pd.read_sql("SELECT * FROM db_model", conn_model)
        conn_model.close()
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível ler a tabela 'db_model' em {db_model_path}: {e}")
        current_df = pd.DataFrame()

    if reference_df.empty or current_df.empty:
        print("Dados insuficientes para calcular drift (referência ou dados de produção estão vazios).")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("<html><body><h1>Relatório de Drift</h1><p>Dados insuficientes para calcular drift (referência ou dados de produção estão vazios).</p></body></html>")
        print(f"⚠️ Relatório de aviso criado em: {output_path}")
        return output_path

    print(f"Dados carregados. Referência: {len(reference_df)} linhas | Produção: {len(current_df)} linhas")

    target_column = os.getenv("TARGET_COLUMN", "vl_glosa")
    
    # Features usadas pelo modelo de Machine Learning
    numerical_features = ['vl_informado', 'qt_informado']
    categorical_features = ['cd_procedimento', 'cd_tipoproduto']

    # Ajuste: Criar coluna de predição na referência igual ao target para evitar erro de Target Drift
    if 'PREVISAO_GLOSA_PELO_IA' not in reference_df.columns:
        reference_df['PREVISAO_GLOSA_PELO_IA'] = reference_df[target_column]
    
    if target_column not in current_df.columns:
        current_df[target_column] = 0.0

    print("Gerando Relatório de Drift (Data Drift e Target Drift)...")
    drift_report = Report(metrics=[
        DataDriftPreset(),
        TargetDriftPreset(),
    ])

    from evidently.pipeline.column_mapping import ColumnMapping
    cm = ColumnMapping()
    cm.target = target_column
    cm.prediction = "PREVISAO_GLOSA_PELO_IA"
    cm.numerical_features = numerical_features
    cm.categorical_features = categorical_features

    drift_report.run(
        reference_data=reference_df,
        current_data=current_df,
        column_mapping=cm
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    drift_report.save_html(output_path)
    print(f"✅ Relatório de Monitoramento salvo com sucesso em: {output_path}")

    # Log para o MLflow
    try:
        setup_mlflow("Monitoramento_Drift")
        with mlflow.start_run(run_name="Evidently_Drift_Analysis"):
            mlflow.log_artifact(output_path, artifact_path="reports")
            # Extrair algumas métricas básicas do report para logar como métricas
            # (Simplificado: apenas confirmando que o report foi gerado)
            mlflow.log_metric("drift_report_generated", 1.0)
            print("📊 Relatório enviado para o MLflow com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para o MLflow: {e}")

    return output_path

if __name__ == "__main__":
    run_drift_detection()


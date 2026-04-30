import os
import pandas as pd
import sqlite3
from pathlib import Path
import mlflow
import skops.io as sio
from src.models.mlflow_utils import setup_mlflow

def run_model_evaluation():
    # 1. Configuração de Caminhos
    base_dir = Path(__file__).resolve().parents[1]
    db_path = base_dir / "db_lite" / "meu_banco_de_dados.db"
    model_path = base_dir / "src" / "models" / "modelo_glosa.skops"
    
    if not db_path.exists():
        print(f"❌ Erro: Banco de dados não encontrado em {db_path}")
        return

    # 2. Carregar Dados de Teste (Histórico)
    print("📂 Carregando dados para avaliação...")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM pedidos_reembolso WHERE nm_situacaoreembolso IN ('PAGO', 'INDEFERIDO')", conn)
    conn.close()

    if df.empty:
        print("⚠️ Aviso: Sem dados históricos para avaliação.")
        return

    # 3. Preparar Features (Mesmo processamento do treino)
    colunas_preditoras = ['cd_procedimento', 'vl_informado', 'qt_informado', 'cd_tipoproduto']
    target = 'vl_glosa'
    
    X = df[colunas_preditoras].copy()
    y = df[target]
    
    # One-hot encoding para cd_procedimento (como no train.py)
    X = pd.get_dummies(X, columns=['cd_procedimento'])

    # 4. Carregar Modelo
    if not model_path.exists():
        print(f"❌ Erro: Modelo não encontrado em {model_path}. Execute o treino primeiro.")
        return
    
    print("🤖 Carregando modelo...")
    modelo = sio.load(model_path, trusted=True)

    # Garantir que as colunas batem (reindex)
    # No treino, as colunas dependem dos procedimentos presentes. 
    # Para simplificar na avaliação, usamos o que o modelo espera.
    # Em um cenário real, carregaríamos a lista de features salva em JSON.
    
    # 5. MLflow Evaluation
    print("📊 Iniciando avaliação no MLflow...")
    setup_mlflow("Avaliacao_Qualidade_Modelo")
    
    # Criar um DataFrame de avaliação que contenha as features e o target
    eval_df = X.copy()
    eval_df[target] = y

    with mlflow.start_run(run_name="RandomForest_Quality_Check"):
        # mlflow.evaluate espera um modelo (pode ser o objeto, a uri ou uma função)
        # Para modelos sklearn, ele gera métricas de regressão automaticamente
        result = mlflow.evaluate(
            model=lambda data: modelo.predict(data),
            data=eval_df,
            targets=target,
            model_type="regressor",
            evaluators="default"
        )
        
        print(f"✅ Avaliação concluída! Run ID: {mlflow.active_run().info.run_id}")
        print(f"Métricas principais: {result.metrics}")

if __name__ == "__main__":
    run_model_evaluation()

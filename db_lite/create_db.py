import sqlite3
import os
import sys
from pathlib import Path
import pandas as pd
import mlflow

# Adiciona a pasta atual ao sys.path para importar data_base.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from data_base import generate_mock_data
except ImportError as e:
    print(f"Erro ao importar data_base: {e}")
    sys.exit(1)

# Define o caminho para o banco de dados dentro da pasta atual
db_dir = Path(__file__).resolve().parent
db_path = db_dir / "meu_banco_de_dados.db"
db_path.parent.mkdir(parents=True, exist_ok=True)

# Conecta ao banco de dados SQLite. 
conn = sqlite3.connect(db_path)

# Gera 1 linha para garantir que o DataFrame mapeie as colunas corretamente
df_vazio = generate_mock_data(1)

# Salva a tabela vazia (filtrando 0 linhas na inserção) para criar ou "zerar/limpar" a estrutura 
df_vazio.iloc[0:0].to_sql('pedidos_reembolso', conn, if_exists='replace', index=False)

# Cria a tabela db_model completamente vazia para os resultados da inferência
df_db_model = df_vazio.iloc[0:0].copy()
df_db_model['PREVISAO_GLOSA_PELO_IA'] = pd.Series(dtype='float64')
df_db_model['vl_previsao'] = pd.Series(dtype='float64')
df_db_model.to_sql('db_model', conn, if_exists='replace', index=False)

# Inicializa o esquema do MLflow no banco de dados separado
mlflow.set_tracking_uri(f"sqlite:///{db_dir}/mlflow.db")
# Criar o experimento garante que o MLflow inicialize as tabelas internas se não existirem
mlflow.set_experiment("Previsor_de_Glosas")

conn.commit()
print(f"Banco de dados e tabelas ('pedidos_reembolso', 'db_model' e MLflow) inicializados com sucesso em: {db_path}")

conn.close()
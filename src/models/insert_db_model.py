import pandas as pd
from pathlib import Path
import skops.io as sio
import sqlite3
import json
import sys

caminho_base = Path(__file__).resolve().parents[2]
caminho_db = caminho_base / "db_lite" / "meu_banco_de_dados.db"

print(f"Buscando novos pedidos no banco de dados em: {caminho_db}")
conn = sqlite3.connect(caminho_db)
df = pd.read_sql("SELECT * FROM pedidos_reembolso WHERE nm_situacaoreembolso = 'EM ANALISE'", conn)

if len(df) == 0:
    print("Nenhum pedido marcado como 'EM ANALISE' no banco de dados.")
    conn.close()
    sys.exit(0)

# Importando arquivos do treinamento
caminho_modelo = Path(__file__).resolve().parent / "modelo_glosa.skops"
caminho_features = Path(__file__).resolve().parent / "features_modelo.json"

try:
    tipos_nao_confiaveis = sio.get_untrusted_types(file=caminho_modelo)
    modelo = sio.load(caminho_modelo, trusted=tipos_nao_confiaveis)
except Exception as e:
    print(f"❌ Erro ao carregar modelo Skops: {e}")
    conn.close()
    sys.exit(1)

try:
    with open(caminho_features, 'r', encoding='utf-8') as f:
        features_esperadas = json.load(f)
except Exception as e:
    print(f"❌ Erro ao ler schema de features json: {e}")
    conn.close()
    sys.exit(1)

print(f"Realizando inferência sobre {len(df)} pedidos pendentes...")

colunas_preditoras = ['cd_procedimento', 'vl_informado', 'qt_informado', 'cd_tipoproduto']

X_futuro = df[colunas_preditoras].copy()
X_futuro = pd.get_dummies(X_futuro, columns=['cd_procedimento'])

# Ajuste automático do schema para ficar estritamente igual ao do treino
X_futuro = X_futuro.reindex(columns=features_esperadas, fill_value=0)

previsoes = modelo.predict(X_futuro)

df_final = df.copy()
df_final.loc[:, 'PREVISAO_GLOSA_PELO_IA'] = previsoes
df_final.loc[:, 'vl_previsao'] = previsoes.round(2)

# Salvar o log final da inferência em um banco separado para evitar conflitos de checkout do DVC
caminho_db_model = caminho_base / "db_lite" / "meu_banco_de_dados_model.db"
conn_model = sqlite3.connect(caminho_db_model)
df_final.to_sql('db_model', conn_model, if_exists='append', index=False)
conn_model.close()

conn.close()
print(f"✅ Inserção concluída! {len(df_final)} registros processados e inseridos no banco de resultados: {caminho_db_model}")

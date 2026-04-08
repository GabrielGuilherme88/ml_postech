import pandas as pd
from pathlib import Path
import skops.io as sio
import json
import mlflow
import mlflow.sklearn

caminho_base = Path(__file__).resolve().parents[2]
caminho_arquivo = caminho_base / "build" / "raw" / "dados_reembolso_hipoteticos.csv"

print(f"Buscando arquivo em: {caminho_arquivo}")

df = pd.read_csv(caminho_arquivo, sep=';')

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pandas as pd

# 1. Expandindo nossas Variáveis Preditivas (X) e nosso Alvo (y)
colunas_preditoras = ['cd_procedimento', 'vl_informado', 'qt_informado', 'cd_tipoproduto']
alvo = 'vl_glosa'

# 2. Separando "O Passado/Decidido" vs "O Futuro/Em Análise"
df_historico = df[df['nm_situacaoreembolso'].isin(['PAGO', 'INDEFERIDO'])].copy()
df_futuro_analise = df[df['nm_situacaoreembolso'] == 'EM ANALISE'].copy()

print(f"Tamanho da Base Histórica para Treinar: {len(df_historico)} pedidos")
print(f"Tamanho da Base EM ANALISE para Prever: {len(df_futuro_analise)} pedidos\n")

X_historico = df_historico[colunas_preditoras].copy()
y_historico = df_historico[alvo]

X_historico = pd.get_dummies(X_historico, columns=['cd_procedimento'])

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X_historico, y_historico, test_size=0.2, random_state=42
)

mlflow.set_tracking_uri(f"sqlite:///{caminho_base}/mlflow.db")
mlflow.set_experiment("Previsor_de_Glosas")

parametros_rf = {"n_estimators": 100, "random_state": 42}

##mlflow

with mlflow.start_run(run_name="RandomForest_Glosas_v1") as run:
    mlflow.log_params(parametros_rf)
    
    modelo = RandomForestRegressor(**parametros_rf)
    modelo.fit(X_treino, y_treino)

    previsoes_teste = modelo.predict(X_teste)
    mae = mean_absolute_error(y_teste, previsoes_teste)
    
    mlflow.log_metric("MAE", mae)
    mlflow.sklearn.log_model(modelo, "modelo_glosa")
    
    print(f"Desempenho no Histórico (O quão bem ele está lembrando) -> MAE: R$ {mae:.2f}")
    print(f"🔗 MLflow Run ID salvo: {run.info.run_id}")

# Preparando a base que queremos adivinhar o futuro:
X_futuro = df_futuro_analise[colunas_preditoras].copy()
X_futuro = pd.get_dummies(X_futuro, columns=['cd_procedimento'])

X_futuro = X_futuro.reindex(columns=X_historico.columns, fill_value=0)

df_futuro_analise.loc[:, 'PREVISAO_GLOSA_PELO_IA'] = modelo.predict(X_futuro)

df_futuro_analise.loc[:, 'vl_previsao'] = modelo.predict(X_futuro).round(2)

print("\n--- PREVIEW DA FILA 'EM ANÁLISE' COM O JULGAMENTO DA NOSSA IA ---")

# -------------------------------------------------------------
# 6. EXPORTANDO O MODELO PARA A API (COM SKOPS)
# -------------------------------------------------------------

caminho_salvar_modelo = Path(__file__).resolve().parent / "modelo_glosa.skops"
caminho_salvar_features = Path(__file__).resolve().parent / "features_modelo.json"

sio.dump(modelo, caminho_salvar_modelo)

with open(caminho_salvar_features, 'w', encoding='utf-8') as f:
    json.dump(list(X_historico.columns), f)

print(f"\n🛡️ Modelo salvo com Skops em: {caminho_salvar_modelo}")
print(f"📦 Features salvas com JSON em: {caminho_salvar_features}")

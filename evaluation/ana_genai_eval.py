import json
import asyncio
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import mlflow
from mlflow.genai import evaluate
from mlflow.genai.scorers import Correctness

# Importar o agente Ana do projeto
from src.agent.agentes_langgraph.agent import run as run_ana

# Carregar ambiente
load_dotenv()

# Configuração do MLflow
from src.models.mlflow_utils import setup_mlflow
setup_mlflow("Avaliacao_GenAI_Ana")

def predict_ana(question: str) -> str:
    """Função de predição síncrona para o MLflow."""
    print(f"🤔 Ana processando: {question}")
    try:
        # Executa o agente assíncrono de forma síncrona
        result = asyncio.run(run_ana(question))
        return result.output
    except Exception as e:
        return f"Erro na Ana: {e}"

def run_genai_evaluation():
    # 1. Carregar Golden Set
    base_dir = Path(__file__).resolve().parents[1]
    golden_set_path = base_dir / "data" / "golden_set" / "golden_set.json"
    
    if not golden_set_path.exists():
        print(f"❌ Golden Set não encontrado em: {golden_set_path}")
        return

    with open(golden_set_path, "r", encoding="utf-8") as f:
        golden_set = json.load(f)

    # 2. Formatar dados para o mlflow.genai.evaluate
    # O MLflow espera uma lista de dicts com 'inputs' e 'expectations'
    eval_dataset = []
    for item in golden_set[:5]:  # Usando apenas 5 para teste rápido
        eval_dataset.append({
            "inputs": {"question": item["query"]},
            "expectations": {"expected_response": item["expected_answer"]}
        })

    print(f"🚀 Iniciando mlflow.genai.evaluate com {len(eval_dataset)} casos...")
    print("⚠️  Nota: Isso requer OPENAI_API_KEY configurada para o juiz (Correctness).")

    try:
        with mlflow.start_run(run_name="GenAI_Correctness_Check"):
            results = evaluate(
                data=eval_dataset,
                predict_fn=predict_ana,
                scorers=[Correctness()],
            )
            
            print("\n✅ Avaliação GenAI concluída!")
            print(results.metrics)
            print("\nConfira os detalhes na aba 'Evaluation' do MLflow UI.")
            
    except Exception as e:
        print(f"❌ Erro durante a avaliação: {e}")
        print("\nDica: Verifique se sua OPENAI_API_KEY é válida no arquivo .env.")

if __name__ == "__main__":
    run_genai_evaluation()

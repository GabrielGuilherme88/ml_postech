import sys
import os
from pathlib import Path

# Adicionar a raiz do projeto ao PYTHONPATH para encontrar o módulo 'src'
root_path = Path(__file__).resolve().parents[1]
sys.path.append(str(root_path))

import json
import logging
import asyncio
import pandas as pd
from dotenv import load_dotenv

import mlflow
from mlflow.metrics.genai import answer_relevance, answer_correctness

from src.agent.agentes_langgraph import agent

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente (.env)
load_dotenv()

def avaliar_ana(inputs: pd.Series) -> list[str]:
    """Wrapper para rodar o agente Ana em cada pergunta."""
    respostas = []
    
    # O MLflow passa os inputs como uma Series do Pandas
    for pergunta in inputs:
        logger.info(f"Testando a Ana com a pergunta: '{pergunta}'")
        try:
            # Como o MLflow roda de forma síncrona, executamos o async aqui
            result = asyncio.run(agent.run(pergunta))
            respostas.append(result.output)
        except Exception as e:
            logger.error(f"Erro ao processar: {e}")
            respostas.append("ERRO DE EXECUÇÃO")
            
    return respostas

def run_mlflow_evaluation(golden_set_path: str):
    if not os.path.exists(golden_set_path):
        logger.error(f"Arquivo Golden Set não encontrado: {golden_set_path}")
        return

    with open(golden_set_path, "r", encoding="utf-8") as f:
        golden_set = json.load(f)

    logger.info(f"Iniciando avaliação MLflow sobre {len(golden_set)} casos...")
    
    # Extrair perguntas e respostas esperadas
    perguntas = [item["query"] for item in golden_set]
    respostas_esperadas = [item["expected_answer"] for item in golden_set]

    # Criar DataFrame que o MLflow espera
    df = pd.DataFrame({
        "inputs": perguntas,
        "ground_truth": respostas_esperadas
    })

    # Configurar MLflow usando o utilitário do projeto
    from src.models.mlflow_utils import setup_mlflow
    setup_mlflow("Avaliacao_Agente_Ana")

    # Juízes do MLflow (usam OPENAI_API_KEY do .env)
    logger.info("Executando mlflow.evaluate() com LLM-as-a-judge via OpenRouter...")
    
    # Definir o modelo de juiz (judge) para o OpenRouter
    judge_model = "openai/gpt-4o-mini"
    model_uri = f"openai:/{judge_model}"

    with mlflow.start_run(run_name="Golden_Set_Evaluation"):
        resultados = mlflow.evaluate(
            model=avaliar_ana,
            data=df,
            targets="ground_truth",
            model_type="question-answering",
            extra_metrics=[
                answer_relevance(model=model_uri),
                answer_correctness(model=model_uri)
            ]
        )
        
        print("\n" + "="*50)
        print("📊 RESULTADOS DA AVALIAÇÃO MLFLOW (OPENROUTER JUDGE)")
        print("="*50)
        for name, value in resultados.metrics.items():
            print(f"{name:30}: {value:.4f}")
        print("="*50)
        print("✅ Verifique o painel do MLflow (aba Evaluation/Traces) para ver os detalhes!")

if __name__ == "__main__":
    GOLDEN_SET = "data/golden_set/golden_set.json"
    run_mlflow_evaluation(GOLDEN_SET)

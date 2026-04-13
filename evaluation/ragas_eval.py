import json
import logging
import asyncio
import os
from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from typing import Callable, Any
from src.agent.agentes_langgraph import agent

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente (.env)
load_dotenv()

async def get_agent_response(question: str) -> tuple[str, list[str]]:
    """Wrapper para chamar o agente e retornar (resposta, contextos)."""
    try:
        result = await agent.run(question)
        return result.output, result.context
    except Exception as e:
        logger.error(f"Erro ao processar pergunta '{question}': {e}")
        return "ERRO DE EXECUÇÃO", []

async def run_evaluation(golden_set_path: str):
    """Executa a avaliação completa sobre o Golden Set."""
    if not os.path.exists(golden_set_path):
        logger.error(f"Arquivo Golden Set não encontrado: {golden_set_path}")
        return

    with open(golden_set_path, "r", encoding="utf-8") as f:
        golden_set = json.load(f)

    logger.info(f"Iniciando avaliação sobre {len(golden_set)} casos...")
    
    results = []
    for i, item in enumerate(golden_set):
        logger.info(f"Processando caso {i+1}/{len(golden_set)}: {item['query']}")
        answer, contexts = await get_agent_response(item["query"])
        results.append({
            "question": item["query"],
            "answer": answer,
            "contexts": contexts,
            "ground_truth": item["expected_answer"],
        })

    # Criar dataset do HuggingFace para o Ragas
    dataset = Dataset.from_list(results)

    logger.info("Calculando métricas RAGAS (aguardando LLM Judge)...")
    
    # Nota: Ragas exige OPENAI_API_KEY no ambiente para estas métricas
    try:
        scores = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )
        
        metrics = {
            "faithfulness": float(scores["faithfulness"]),
            "answer_relevancy": float(scores["answer_relevancy"]),
            "context_precision": float(scores["context_precision"]),
            "context_recall": float(scores["context_recall"]),
        }
        
        print("\n" + "="*50)
        print("📊 RESULTADOS DA AVALIAÇÃO RAGAS")
        print("="*50)
        for name, value in metrics.items():
            print(f"{name:20}: {value:.4f}")
        print("="*50)
        
        return metrics
    except Exception as e:
        logger.error(f"Falha ao calcular métricas RAGAS: {e}")
        if "OPENAI_API_KEY" not in os.environ:
            logger.warning("DICA: Certifique-se de configurar a OPENAI_API_KEY no arquivo .env")
        return None

if __name__ == "__main__":
    GOLDEN_SET = "data/golden_set/golden_set.json"
    asyncio.run(run_evaluation(GOLDEN_SET))

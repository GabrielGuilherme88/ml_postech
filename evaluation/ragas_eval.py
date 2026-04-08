"""Avaliação do pipeline RAG com RAGAS — 4 métricas obrigatórias."""
import json
import logging
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from typing import Callable, Any

logger = logging.getLogger(__name__)

def evaluate_rag_pipeline(
    golden_set_path: str,
    rag_fn: Callable[[str], tuple[str, list[str]]],
) -> dict[str, float]:
    with open(golden_set_path) as f:
        golden_set = json.load(f)

    results = []
    for item in golden_set:
        answer, contexts = rag_fn(item["query"])
        results.append({
            "question": item["query"],
            "answer": answer,
            "contexts": contexts,
            "ground_truth": item["expected_answer"],
        })

    dataset = Dataset.from_list(results)
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
    logger.info("RAGAS scores: %s", metrics)
    return metrics

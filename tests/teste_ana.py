import asyncio
import sys
import os
from pathlib import Path

# Adicionar a raiz do projeto ao path
sys.path.append(os.getcwd())

from src.agent.agentes_langgraph.agent import run
from src.models.mlflow_utils import setup_mlflow

# Configurar MLflow para o experimento correto
setup_mlflow("Avaliacao_GenAI_Ana")

async def main():
    pergunta = "Me conte mais sobre você?"
    print(f"\n🚀 Testando a Ana com OpenRouter...")
    print(f"❓ Pergunta: {pergunta}")
    print("-" * 30)
    
    try:
        resultado = await run(pergunta)
        print(f"\n✅ Resposta da Ana:\n{resultado.output}")
        print("-" * 30)
        print(f"📊 Detalhes: Duração {resultado.duration_ms}ms | Ferramentas: {resultado.tools_used}")
    except Exception as e:
        print(f"\n❌ Erro ao testar a Ana: {e}")

if __name__ == "__main__":
    asyncio.run(main())

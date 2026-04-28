import asyncio
import sys
from pathlib import Path

# Adiciona o diretório do agente ao sys.path para que o import funcione
path_agente = Path(__file__).resolve().parents[1] / "src" / "agent" / "agentes_langgraph"
sys.path.append(str(path_agente))

try:
    from agent import run
except ImportError as e:
    print(f"❌ Erro ao importar o agente: {e}")
    print(f"Caminho tentado: {path_agente}")
    sys.exit(1)

# Simula perguntas que um gestor faria para a Ana
PERGUNTAS_TESTE = [
    "Olá Ana, pode me dar um resumo das glosas previstas no banco de dados?",
    "Qual o valor total de glosa previsto para a Empresa Alfa Ltda?",
    "Existe algum procedimento com valor de glosa previsto acima de R$ 500? Liste para mim."
]

async def executar_testes():
    print("🚀 Iniciando Testes do Agente de Auditoria...\n")

    for i, pergunta in enumerate(PERGUNTAS_TESTE, 1):
        print(f"--- Teste {i} ---")
        print(f"Pergunta: {pergunta}")
        
        try:
            resultado = await run(pergunta)
            
            print(f"\nResposta da Ana:\n{resultado.output}")
            print(f"\n[Métricas: Passos: {resultado.step_count} | Ferramentas: {', '.join(resultado.tools_used)} | Tempo: {resultado.duration_ms}ms]")
            print("-" * 50 + "\n")
            
        except Exception as e:
            print(f"❌ Erro ao processar pergunta: {e}\n")

if __name__ == "__main__":
    asyncio.run(executar_testes())

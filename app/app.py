from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from typing import List
from src.agent.agentes_langgraph import agent
import structlog
from src.security.guardrails import InputGuardrail
from mlflow_dash import mlflow_app

# Configuração de Logging Estruturado
structlog.configure()
logger = structlog.get_logger()

# Inicialização do Guardrail de Input
input_guardrail = InputGuardrail()

# Tags para organizar o Swagger UI
openapi_tags = [
    {
        "name": "Agente Ana",
        "description": "Endpoints para interagir com o agente de auditoria de glosas.",
    },
    {
        "name": "MLflow",
        "description": "Acesso ao Dashboard de experimentos do MLflow. "
                       "Clique no link abaixo para abrir o dashboard completo: "
                       "[http://localhost:8000/mlflow/](http://localhost:8000/mlflow/)",
    },
    {
        "name": "Infra",
        "description": "Rotas de monitoramento e saúde da API.",
    },
]

# Inicialização do FastAPI
app = FastAPI(
    title="Ana - Auditora de Saúde API",
    description=(
        "API para interação com o agente de análise de glosas médicas.\n\n"
        "- **Agente Ana**: Faça perguntas em linguagem natural sobre glosas e reembolsos.\n"
        "- **MLflow**: Visualize os experimentos e métricas dos modelos treinados.\n"
        "- **Frontend**: Acesse a interface completa em [http://localhost:8000/](http://localhost:8000/)"
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Adicionando CORS para permitir integração com frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montando o Dashboard do MLflow na rota /mlflow
app.mount("/mlflow", mlflow_app)

# ---------------------------------------------------------------------------
# Modelos de Dados (Schemas)
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    question: str = Field(..., example="Qual o total de glosas previsto para a Empresa Alfa?")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Resposta em linguagem natural gerada pela LLM")
    tools_used: List[str] = Field(..., description="Lista de ferramentas utilizadas pelo agente")
    step_count: int = Field(..., description="Quantidade de passos executados")
    duration_ms: int = Field(..., description="Tempo total de execução em milissegundos")

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Interface Frontend (Importado de htm.py)
# ---------------------------------------------------------------------------

from htm import HTML_CONTENT

# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["Agente Ana"])
async def root():
    """Retorna o frontend estilizado da Ana."""
    return HTML_CONTENT

@app.get("/health", tags=["Infra"])
async def health_check():
    """Verifica a integridade da API. Retorna `healthy` se o agente estiver pronto."""
    return {"status": "healthy", "agent": "Ana"}

@app.get(
    "/mlflow-ui",
    tags=["MLflow"],
    summary="Redireciona para o MLflow Dashboard",
    description=(
        "Redireciona para o Dashboard interativo do MLflow, onde é possível "
        "visualizar experimentos, métricas (MAE, RMSE), parâmetros do modelo "
        "e artefatos registrados durante o treinamento do `Previsor_de_Glosas`.\n\n"
        "O dashboard completo está disponível em: "
        "[http://localhost:8000/mlflow/](http://localhost:8000/mlflow/)"
    ),
    response_class=RedirectResponse,
    status_code=302,
)
async def mlflow_redirect():
    """Redireciona para o Dashboard do MLflow com todos os experimentos registrados."""
    return RedirectResponse(url="/mlflow/")

@app.post("/ask", response_model=QueryResponse, tags=["Agente Ana"])
async def ask_ana(request: QueryRequest):
    """
    Endpoint principal para fazer perguntas à Ana.
    O agente irá consultar o banco de dados e gerar uma resposta explicativa.
    """
    log = logger.bind(question=request.question)
    
    # 1. Validação de Input (Guardrails)
    is_safe, message = input_guardrail.validate(request.question)
    if not is_safe:
        log.warning("input_blocked", reason=message)
        raise HTTPException(status_code=400, detail=message)

    try:
        log.info("processing_request")
        # Executa o agente de forma assíncrona
        result = await agent.run(request.question)
        
        log.info("request_completed", 
                 duration_ms=result.duration_ms, 
                 tools=result.tools_used)

        return QueryResponse(
            answer=result.output,
            tools_used=result.tools_used,
            step_count=result.step_count,
            duration_ms=result.duration_ms
        )
    except Exception as e:
        log.error("agent_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro interno no agente: {str(e)}")

# ---------------------------------------------------------------------------
# Execução Local
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    # Executa o servidor na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
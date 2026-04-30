from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from typing import List
import structlog
import os
import ast
import operator
from src.agent.agentes_langgraph import agent
from src.security.guardrails import InputGuardrail
from .mlflow_dash import mlflow_app
from src.models.mlflow_utils import setup_mlflow
import mlflow
from prometheus_fastapi_instrumentator import Instrumentator
from .htm import HTML_CONTENT

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}
_SAFE_FUNCS = {"abs": abs, "round": round}

def _safe_eval(node: ast.AST):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _SAFE_FUNCS:
        return _SAFE_FUNCS[node.func.id](*[_safe_eval(a) for a in node.args])
    raise ValueError("Expressão insegura")

try:
    from langfuse import Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        host=os.getenv("LANGFUSE_HOST", "http://localhost:3001")
    )
    LANGFUSE_ENABLED = bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
except Exception:
    langfuse = None
    LANGFUSE_ENABLED = False

# Configuração de Logging Estruturado
structlog.configure()
logger = structlog.get_logger()

# Inicialização do Guardrail de Input
input_guardrail = InputGuardrail()

# Inicialização do MLflow Tracking (para Traces da GenAI)
APP_VERSION = "1.0.0-OpenRouter"
setup_mlflow("Avaliacao_GenAI_Ana")

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

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

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
# Rotas e Lógica da API
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

@app.get("/mlflow-ui", tags=["MLflow"])
async def mlflow_redirect():
    """Redireciona para o Dashboard do MLflow."""
    return RedirectResponse(url="/mlflow/")

@app.get("/drift", response_class=HTMLResponse, tags=["Infra"])
async def drift_report():
    """Exibe o relatório de Data Drift gerado pelo Evidently."""
    caminho_report = os.path.join(os.getcwd(), "reports", "drift_report.html")
    if not os.path.exists(caminho_report):
        return HTMLResponse("<h1>Relatório não gerado</h1><p>Execute 'make drift' para gerar o relatório.</p>", status_code=404)
    
    with open(caminho_report, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/ask", response_model=QueryResponse, tags=["Agente Ana"])
async def ask_ana(request: QueryRequest):
    """
    Endpoint principal para fazer perguntas à Ana.
    O agente irá consultar o banco de dados e gerar uma resposta explicativa.
    """
    log = logger.bind(question=request.question)
    
    is_safe, message = input_guardrail.validate(request.question)
    if not is_safe:
        log.warning("input_blocked", reason=message)
        raise HTTPException(status_code=400, detail=message)

    if LANGFUSE_ENABLED:
        trace = langfuse.trace(name="ask_ana")
        trace.input({"question": request.question})

    try:
        log.info("processing_request")
        result = await agent.run(request.question)
        
        log.info("request_completed", 
                 duration_ms=result.duration_ms, 
                 tools=result.tools_used)

        if LANGFUSE_ENABLED:
            trace.output({"answer": result.output, "tools": result.tools_used})
            trace.metrics({
                "latency_ms": result.duration_ms,
                "step_count": result.step_count
            })

        return QueryResponse(
            answer=result.output,
            tools_used=result.tools_used,
            step_count=result.step_count,
            duration_ms=result.duration_ms
        )
    except Exception as e:
        log.error("agent_error", error=str(e))
        if LANGFUSE_ENABLED:
            trace.error(str(e))
        raise HTTPException(status_code=500, detail=f"Erro interno no agente: {str(e)}")

# ---------------------------------------------------------------------------
# Execução Local
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    # Executa o servidor na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
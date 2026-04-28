"""
Agente de Análise de Glosas — LiteLlama Local
Arquitetura: Consulta SQL direta + LiteLlama para resposta em linguagem natural.
"""

from __future__ import annotations

import ast
import operator
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator
import structlog

logger = structlog.get_logger()

import os
import torch
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.security.guardrails import OutputGuardrail
import mlflow

# Inicialização do Guardrail de Output
output_guardrail = OutputGuardrail()

# Permite carregar modelos no formato .bin legado (necessário para LiteLlama-460M)
# O CVE-2025-32434 é mitigado aqui pois estamos carregando de fonte conhecida e confiável
os.environ["TRUST_REMOTE_CODE"] = "1"

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------

DB_PATH = Path(__file__).resolve().parents[3] / "db_lite" / "meu_banco_de_dados.db"
MODEL_PATH = "ahxt/LiteLlama-460M-1T"
MAX_NEW_TOKENS = 200

# ---------------------------------------------------------------------------
# Tipos de retorno públicos
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    """Resultado completo de uma execução do agente."""
    output: str
    tools_used: list[str]
    context: list[str]
    token_count: int
    step_count: int
    duration_ms: int

@dataclass
class AgentEvent:
    """Evento emitido durante a execução em streaming do agente."""
    type: str
    data: dict[str, Any]

# ---------------------------------------------------------------------------
# Banco de dados (Singleton)
# ---------------------------------------------------------------------------

_db_connection: sqlite3.Connection | None = None

def _get_db() -> sqlite3.Connection:
    global _db_connection
    if _db_connection is None:
        if not DB_PATH.exists():
            raise FileNotFoundError(
                f"Banco de dados não encontrado em: {DB_PATH}. "
                "Certifique-se de ter rodado 'make pipeline' primeiro."
            )
        _db_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _db_connection.row_factory = sqlite3.Row
    return _db_connection

# ---------------------------------------------------------------------------
# Ferramenta de consulta SQL
# ---------------------------------------------------------------------------

@mlflow.trace(name="query_db")
def _query_db(sql: str) -> str:
    """Executa uma query SELECT no banco de dados e retorna o resultado como string."""
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        return "ERRO: Apenas consultas SELECT são permitidas."
    try:
        conn = _get_db()
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        if not rows:
            return "Nenhum resultado encontrado."
        col_names = [d[0] for d in cursor.description]
        lines = [" | ".join(col_names)]
        lines.append("-" * len(lines[0]))
        for row in rows:
            lines.append(" | ".join(str(v) for v in row))
        lines.append(f"\n({len(rows)} linha(s))")
        return "\n".join(lines)
    except Exception as e:
        return f"ERRO SQL: {e}"

# ---------------------------------------------------------------------------
# Calculadora segura via AST
# ---------------------------------------------------------------------------

_SAFE_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}
_SAFE_FUNCS = {"abs": abs, "round": round, "min": min, "max": max, "sum": sum}

def _safe_eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant): return node.value
    if isinstance(node, ast.BinOp): return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp): return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _SAFE_FUNCS:
        return _SAFE_FUNCS[node.func.id](*[_safe_eval(a) for a in node.args])
    raise ValueError(f"Expressão não suportada: {ast.dump(node)}")

def _calculate(expression: str) -> str:
    try:
        return str(_safe_eval(ast.parse(expression.strip(), mode="eval").body))
    except Exception as e:
        return f"ERRO: {e}"

# ---------------------------------------------------------------------------
# Extração automática de SQL da pergunta
# ---------------------------------------------------------------------------

def _build_sql_from_question(question: str) -> str:
    """
    Heurística simples para identificar o tipo de pergunta e 
    montar a query correspondente. Para um modelo pequeno, essa
    abordagem é mais confiável que deixar o LLM decidir.
    """
    q = question.lower()

    # Busca por empresa específica
    empresas_conhecidas = ["empresa alfa ltda", "beta tech s.a.", "gamma servicos"]
    for empresa in empresas_conhecidas:
        if empresa in q:
            return (
                f"SELECT nm_empresa, nm_beneficiario, nm_prestador, "
                f"vl_informado, PREVISAO_GLOSA_PELO_IA, vl_previsao "
                f"FROM db_model WHERE LOWER(nm_empresa) LIKE '%{empresa}%' LIMIT 20"
            )

    # Busca por maiores glosas
    if any(w in q for w in ["maior", "mais alto", "top", "alta", "acima"]):
        return (
            "SELECT nm_beneficiario, nm_empresa, nm_prestador, vl_informado, "
            "PREVISAO_GLOSA_PELO_IA, vl_previsao "
            "FROM db_model ORDER BY PREVISAO_GLOSA_PELO_IA DESC LIMIT 10"
        )

    # Total ou soma
    if any(w in q for w in ["total", "soma", "somando", "quanto"]):
        return (
            "SELECT nm_empresa, "
            "ROUND(SUM(PREVISAO_GLOSA_PELO_IA), 2) as total_glosa_prevista, "
            "COUNT(*) as qtd_pedidos "
            "FROM db_model GROUP BY nm_empresa ORDER BY total_glosa_prevista DESC"
        )

    # Fallback: resumo geral
    return (
        "SELECT nm_empresa, COUNT(*) as qtd_pedidos, "
        "ROUND(AVG(vl_informado), 2) as media_valor_solicitado, "
        "ROUND(AVG(PREVISAO_GLOSA_PELO_IA), 2) as media_glosa_prevista, "
        "ROUND(SUM(PREVISAO_GLOSA_PELO_IA), 2) as total_glosa_prevista "
        "FROM db_model GROUP BY nm_empresa"
    )

# ---------------------------------------------------------------------------
# Modelo LiteLlama (Singleton)
# ---------------------------------------------------------------------------

_model = None
_tokenizer = None

def _get_model():
    global _model, _tokenizer
    if _model is None:
        print(f"[Carregando modelo {MODEL_PATH}... isso pode levar alguns instantes]")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
        _model.eval()
        print("[Modelo carregado com sucesso!]")
    return _model, _tokenizer

# ---------------------------------------------------------------------------
# Geração de resposta
# ---------------------------------------------------------------------------

@mlflow.trace(name="generate_response")
def _generate_response(question: str, data: str) -> str:
    """
    Monta o prompt com contexto dos dados do banco 
    e gera a resposta com o LiteLlama.
    """
    model, tokenizer = _get_model()

    prompt = (
        "Você é Ana, uma auditora de saúde. Responda em português com base nos dados.\n\n"
        f"Dados do banco de dados:\n{data}\n\n"
        f"Pergunta: {question}\nResposta:"
    )

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

    with torch.no_grad():
        tokens = model.generate(
            input_ids,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decodifica apenas os tokens gerados (sem o prompt)
    generated = tokens[0][input_ids.shape[-1]:]
    return tokenizer.decode(generated.tolist(), skip_special_tokens=True).strip()

# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------

@mlflow.trace(name="agent_run")
async def run(message: str) -> AgentResult:
    """Executa o agente de forma assíncrona e retorna o resultado completo."""
    start_time = time.monotonic()
    tools_used: list[str] = []

    log = logger.bind(message=message)
    
    # 1. Monta e executa a query
    sql = _build_sql_from_question(message)
    log.info("query_generation", sql=sql)
    
    tools_used.append("search_reimbursement_data")
    data = _query_db(sql)
    log.info("db_query_completed", data_length=len(data))

    # 2. Gera resposta com o LiteLlama (roda em thread separada para não travar o loop)
    log.info("llm_generation_start")
    output_raw = await asyncio.to_thread(_generate_response, message, data)
    log.info("llm_generation_completed")

    # 3. Sanitização de Output (Guardrails)
    output = output_guardrail.sanitize(output_raw)

    duration_ms = int((time.monotonic() - start_time) * 1000)

    return AgentResult(
        output=output,
        tools_used=tools_used,
        context=[data],
        token_count=0,  # Não disponível via transformers direto
        step_count=2,   # Consulta DB + Geração LLM
        duration_ms=duration_ms,
    )


async def run_stream(message: str) -> AsyncGenerator[AgentEvent, None]:
    """Versão streaming: emite os dados brutos antes da resposta final."""
    start_time = time.monotonic()

    # Passo 1: Consulta ao banco
    sql = _build_sql_from_question(message)
    yield AgentEvent(type="step_start", data={"node": "search_db", "step": 1})
    yield AgentEvent(type="tool_call", data={"tool": "search_reimbursement_data", "args": {"query": sql}})

    data = _query_db(sql)
    yield AgentEvent(type="tool_result", data={"tool": "search_reimbursement_data", "content": data})

    # Passo 2: Geração da resposta
    yield AgentEvent(type="step_start", data={"node": "generate_response", "step": 2})
    output = _generate_response(message, data)
    yield AgentEvent(type="token", data={"content": output})

    duration_ms = int((time.monotonic() - start_time) * 1000)

    yield AgentEvent(
        type="done",
        data={
            "result": AgentResult(
                output=output,
                tools_used=["search_reimbursement_data"],
                context=[data],
                token_count=0,
                step_count=2,
                duration_ms=duration_ms,
            )
        },
    )

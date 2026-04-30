# 👩‍⚕️ Ana: Auditora de Saúde Inteligente
> **Sistema de Auditoria de Saúde com MLOps, Agentes ReAct e Governança Completa.**

Este projeto é uma solução de ponta a ponta para a auditoria de glosas médicas, combinando Inteligência Artificial (LLMs Locais), Engenharia de Dados e práticas avançadas de MLOps. Desenvolvido para a Fase 05 do Datathon Pós-Tech MLE.

---

## 🛠️ Stack Tecnológica

O projeto utiliza uma arquitetura moderna de microsserviços e ferramentas de governança:

*   **Core AI**: Python 3.10+, LangGraph, LangChain, LiteLlama-460M (HuggingFace).
*   **Serviço de API**: FastAPI, Uvicorn, Pydantic.
*   **Orquestração de Dados**: **Apache Airflow 2.9** (gerenciando pipelines de treinamento e drift).
*   **Versionamento**: **DVC** (Data Version Control) para dados e modelos.
*   **Observabilidade & LLM Ops**:
    *   **MLflow**: Rastreamento de experimentos e registro de modelos.
    *   **Langfuse**: Rastreamento de traces, custos e latência do Agente LLM.
    *   **Prometheus & Grafana**: Métricas de performance da infraestrutura e API.
    *   **Evidently AI**: Detecção de Data Drift e monitoramento de qualidade.
*   **Segurança**: Microsoft Presidio (Anonymization) e Guardrails customizados.
*   **Banco de Dados**: SQLite (Negócio) e PostgreSQL (Airflow & Langfuse).

---

## 💻 Configuração do Ambiente Local

Se desejar executar ou desenvolver o projeto fora do Docker, siga os passos abaixo para configurar seu ambiente:

### 1. Criar e Ativar o Ambiente Virtual
```bash
python -m venv ambi
source ambi/bin/activate
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

---

## 🚀 Como Executar a Infraestrutura (Docker)

O projeto está totalmente conteinerizado. Com um único comando, você sobe toda a stack de auditoria e monitoramento.

### 1. Requisitos Prévios
*   Docker e Docker Compose instalados.
*   Configurar o arquivo `.env` (use o `.env.example` como base).

### 2. Subir o Ecossistema Completo
```bash
docker compose up -d --build
```

### 3. Acessos Rápidos (Dashboard de Controle)

| Serviço | URL | Credenciais |
| :--- | :--- | :--- |
| **Interface da Ana (API)** | [http://localhost:8000](http://localhost:8000) | - |
| **Airflow (Orquestração)** | [http://localhost:8081](http://localhost:8081) | `airflow` / `airflow` |
| **Grafana (Dashboards)** | [http://localhost:3000](http://localhost:3000) | `admin` / `admin` |
| **MLflow (Modelos)** | [http://localhost:5000](http://localhost:5000) | - |
| **drift report** | [http://localhost:8000/drift](http://localhost:8000/drift) | - |


---

## 🔄 Pipeline de Treinamento e Drift

O projeto utiliza o **Airflow** para garantir que o modelo esteja sempre atualizado:

1.  **Prepare Data**: O Airflow dispara o DVC para extrair e processar novos dados do SQLite.
2.  **Training**: O modelo é treinado, versionado e registrado automaticamente no MLflow.
3.  **Drift Analysis**: Periodicamente, o sistema compara os dados de produção com os de treinamento usando **Evidently AI**, gerando relatórios em `reports/`.

Para disparar manualmente o treinamento via Docker (sem o Airflow):
```bash
docker compose --profile training up
```

---

## 📂 Estrutura de Pastas

```text
ml_postech/
├── src/
│   ├── agent/            # Lógica do Agente ReAct (Ana)
│   ├── models/           # Scripts de Treinamento e Inferência
│   ├── security/         # Camada de Guardrails e PII
│   └── monitoring/       # Integração com Evidently e Langfuse
├── airflow/              # DAGs, Logs e Configurações do Airflow
├── configs/              # Configurações de Grafana e Prometheus
├── db_lite/              # Banco de dados de produção (SQLite)
├── tests/                # Suíte de testes (Pytest)
└── pyproject.toml        # Gestão de dependências
```

---

## 🛡️ Governança e Segurança

O projeto segue as diretrizes da **LGPD** e as melhores práticas da **OWASP**:
*   **Anonimização**: Dados sensíveis (PII) são filtrados antes de chegarem ao LLM.
*   **OWASP Mapping**: Documentação completa sobre riscos de segurança em LLMs (em `docs/`).
*   **System Card**: Detalhes sobre vieses e limitações do modelo.

### Execução de Testes de Segurança
Para validar nivel de proteção:
```bash
make -f Makefile.guardrails test
```

---
*Este repositório é parte integrante da avaliação da Fase 05 - Pós-Tech Machine Learning Engineering.*

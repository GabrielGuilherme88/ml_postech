# Datathon Fase 05 - Análise de Glosas com Agentes e MLOps

Sistema de Auditoria de Saúde utilizando LLMs locais e agentes inteligentes para previsão e análise de glosas médicas, desenvolvido como projeto integrador para a Fase 05 do Datathon.

## 🚀 Insights e Diferenciais

- **Ana: Auditora de Saúde Inteligente**: Implementação de um agente ReAct ("Ana") especializado em auditoria médica, capaz de interpretar pedidos de reembolso e prever glosas com base em dados históricos.
- **LiteLlama Local (Eficiência & Privacidade)**: O projeto utiliza o modelo `LiteLlama-460M-1T` rodando 100% localmente via `transformers`. Isso garante:
    - **Custo Zero**: Sem dependência de APIs pagas (OpenAI/Anthropic).
    - **Baixa Latência**: Respostas rápidas sem dependência de rede.
    - **Privacidade (LGPD)**: Os dados de saúde nunca saem do ambiente controlado.
- **Hibridismo Determinístico**: O agente combina o raciocínio natural do LLM com uma camada de ferramentas SQL robusta, permitindo consultas precisas em banco de dados SQLite (`db_lite`) sem perder a flexibilidade da linguagem natural.
- **Segurança "Safe-by-Design"**: 
    - **Guardrails**: Filtros de input/output para detecção de PII (Presidio) e proteção contra injeção de prompts.
    - **Cálculos Seguros**: Uso de processamento via AST para operações matemáticas, mitigando riscos de execução de código arbitrário.
- **Governança MLOps Nível 2**: Pipeline reprodutível com versionamento de dados (DVC), rastreamento de experimentos (MLflow) e automação via Makefile e Docker.

---

## 📂 Estrutura do Projeto

Abaixo, a organização dos diretórios seguindo as melhores práticas de engenharia de software e MLOps:

```text
ml_postech/
├── src/
│   ├── agent/            # Core do Agente (Ana) e lógica LangGraph
│   ├── models/           # Treinamento, baseline e scripts de treinamento
│   ├── security/         # Implementação de Guardrails e OWASP mapping
├── eda jupyter/          # Notebooks de análise estatística e visual (stats.ipynb)
├── evaluation/           # Framework de avaliação (RAGAS e LLM-as-judge)
├── build/                # Artefatos de dados e modelos (gerenciado via DVC)
├── db_lite/              # Armazenamento do banco de dados SQLite local
├── tests/                # Suíte de testes automatizados com pytest
├── mlruns/               # Logs e métricas das execuções do MLflow
├── configs/              # Arquivos YAML de configuração de modelos e monitoramento
├── docs/                 # Model Cards, System Cards e documentação de segurança
├── Makefile              # Comandos de atalho (make train, make serve, make test)
├── Makefile.guardrails   # Testes exclusivos de segurança e guardrails
├── pyproject.toml        # Definição do projeto e dependências (uv/pip)
├── dvc.yaml              # Definição do pipeline de dados e reprodutibilidade
├── docs/                 # Documentação de Governança (LGPD, OWASP, System Card)
└── tarefas_datathon.md   # Guia de progresso e checklist de entrega
```

---

## 🛠️ Tecnologias Principais

- **LLM**: LiteLlama-460M (HuggingFace)
- **Framework de Agentes**: LangGraph / LangChain
- **MLOps**: MLflow, DVC, Docker
- **Data**: Pandas, Scikit-learn, SQLite
- **Avaliação**: Ragas, Evidently (Drift Detection)
- **Segurança**: Presidio (Microsoft), Pandera (Schema Validation)

---

## 🏁 Como Começar (Local)

1. **Instale as dependências**:
   ```bash
   pip install -e .
   ```
2. **Prepare os dados e o banco**:
   ```bash
   make pipeline
   ```
3. **Execute os testes**:
   - Para testes gerais do modelo:
     ```bash
     make test
     ```
   - Para avaliação técnica RAG (RAGAS):
     ```bash
     make eval
     ```
4. **Inicie a API**:
   ```bash
   make serve
   ```

---

## 🐳 Execução via Docker

O projeto está totalmente conteinerizado, permitindo subir a API e toda a stack de monitoramento (MLOps) de forma isolada e reprodutível.

### 1. Configuração Inicial
Certifique-se de ter o Docker instalado e o arquivo `.env` configurado:
```bash
cp .env.example .env  # E edite com suas chaves se necessário
```

### 2. Subir a Stack (API + Monitoramento)
Este comando inicia a API, MLflow, Prometheus e Grafana:
```bash
docker compose up --build -d
```

### 3. Executar o Pipeline de Treinamento
Para rodar o pipeline completo do DVC dentro do ambiente Docker:
```bash
docker compose run --rm training
```

### 4. Acessos Rápidos
- **API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MLflow (Experimentos)**: [http://localhost:5000](http://localhost:5000)
- **Grafana (Dashboards)**: [http://localhost:3000](http://localhost:3000) (admin/admin)
- **Prometheus (Métricas)**: [http://localhost:9090](http://localhost:9090)

---

---
*Este repositório é parte integrante da avaliação da Fase 05 - Pós-Tech Machine Learning Engineering.*

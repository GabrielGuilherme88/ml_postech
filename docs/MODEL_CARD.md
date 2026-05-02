---

# Model Card — Modelo Preditivo de Glosas (Ana)

## Informações do Modelo

| Campo | Valor |
|---|---|
| **Nome** | Ana - Previsão de Glosas |
| **Versão** | 1.0 |
| **Tipo** | Regressão |
| **Framework** | Scikit-learn (RandomForestRegressor) + SKops |
| **Autores** | Equipe de MLOps - Datathon Fase 05 |
| **Data de Treinamento** | Abril de 2026 |
| **Licença** | MIT |

## Descrição

Modelo de Machine Learning baseado em Random Forest para prever o valor provável de glosa (disallowance) em pedidos de reembolso de saúde. Utiliza dados históricos de procedimentos médicos para apoiar as auditorias médicas e identificar discrepâncias financeiras.

## Uso Pretendido

- **Objetivo**: Previsão de valor de glosa para pedidos de reembolso com base em dados de `cd_procedimento` e `vl_informado`.
- **Público-alvo**: Auditores médicos e analistas de faturamento.
- **Cenários de uso**: Triagem automatizada de pedidos, sinalização de anomalias de valores solicitados e apoio à decisão baseada em histórico de pagamentos.
- **NÃO usar para**: Decisão administrativa final e recusa automática de reembolsos sem supervisão de um auditor humano.

## Dados de Treinamento

- **Fonte**: Base histórica de sinistros de saúde (armazenada em `db_lite`).
- **Pipeline**: Processamento de dados e features orquestrado via DVC e Apache Airflow.
- **Features Principais**:
  - `cd_procedimento`: Código do procedimento médico.
  - `vl_informado`: Valor original solicitado para reembolso.
  - E outros atributos técnicos associados ao sinistro.

## Arquitetura

O sistema emprega uma arquitetura composta onde o modelo de ML atua em conjunto com um LLM:
```
Input (Dados do Pedido)
  → Processamento de Features
  → RandomForestRegressor (Baseline ML)
  → Output (Previsão de Glosa)
  → Agente LLM (LiteLlama-460M-1T) para gerar explicação e Chain-of-Thought
```

## Métricas de Desempenho e Monitoramento

A saúde do modelo e a qualidade das previsões são monitoradas utilizando **MLflow** e **Evidently AI**:
- **Monitoramento contínuo**: Avaliação de Performance de Regressão (MAE, RMSE) e Data Drift em ambiente de produção (mlflow evaluate).
- Tolerâncias operacionais são definidas no pipeline de treinamento garantindo precisão aceitável.

## Limitações

1. **Dependência Histórica**: A precisão é limitada pela qualidade da base histórica de dados. Práticas de faturamento inteiramente novas podem apresentar predições menos confiáveis até o retreino.
2. **Capacidade do LLM**: O componente explicativo (LiteLlama 460M) pode apresentar dificuldades em lógicas extremamente complexas.
3. **Eventos Extremos**: Fraudes sistêmicas não vistas no conjunto de treino podem ser difíceis de capturar na fase preditiva.

## Viés e Fairness

- **Proteção a Atributos Sensíveis**: O modelo baseia-se unicamente em características de faturamento e regras do procedimento. Não inclui variáveis como idade, gênero ou raça na tomada de decisão.
- **Mitigação**: O modelo foca em dados puramente técnicos e financeiros e é constantemente auditado (Drift detection) para garantir a paridade e consistência entre diversas classes de prestadores e procedimentos.

## Considerações Éticas

- As predições são geradas para fins de "Apoio à Decisão" e necessitam de uma pessoa no ciclo (Human-in-the-loop).
- A interface de predição é configurada para exibir as variáveis mais impactantes (Feature Importance) e a cadeia de pensamento (Thought) promovendo total transparência.

## Rastreabilidade

- **Rastreabilidade de Experimentos**: Via MLflow
- **Gestão de Artefatos**: Serialização segura via `skops` e versionamento de dados com DVC.

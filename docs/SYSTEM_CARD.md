# System Card — Auditora de Saúde Inteligente (Ana)

**Versão:** 1.0  
**Data:** Abril de 2026  
**Status**: Em produção (Beta)

## 1. Visão Geral do Sistema
O sistema "Ana" é um agente inteligente projetado para auxiliar auditores médicos na análise de pedidos de reembolso de saúde. Ele utiliza um modelo de Machine Learning (Random Forest) para prever o valor provável de glosa e um LLM local (LiteLlama) para fornecer explicações e insights sobre os dados.

## 2. Modelos e Arquitetura
- **LLM**: LiteLlama-460M-1T (local).
- **ML Baseline**: RandomForestRegressor (Scikit-learn) com serialização via SKops (segurança).
- **Backend**: FastAPI / LangGraph.
- **Banco de Dados**: SQLite.

## 3. Escopo e Limitações
### Casos de Uso Pretendidos:
- Triagem automatizada de pedidos de reembolso.
- Identificação de discrepâncias em valores solicitados vs. históricos.
- Apoio à decisão baseada em dados históricos.

### Limitações:
- **Não substitui o auditor humano**: A "Final Answer" da Ana é um auxílio, não uma decisão administrativa final.
- **LiteLlama Contexto**: O modelo de 460M parâmetros pode ter dificuldades com raciocínios lógicos complexos ou longos diálogos.
- **Dependência de Dados**: A precisão da previsão de glosa é estritamente dependente da qualidade da base histórica no `db_lite`.

## 4. Explicabilidade (Interpretability)
Para garantir a confiança do auditor:
- **Feature Importance**: O modelo de ML expõe as variáveis mais impactantes (ex: `cd_procedimento` e `vl_informado`).
- **Chain-of-Thought**: O agente é configurado para mostrar seu "Thought", permitindo que o auditor entenda quais ferramentas SQL foram chamadas e quais dados foram retornados antes da conclusão.

## 5. Fairness e Viés (Fairness Analysis)
- **Atributos Sensíveis**: O modelo não utiliza gênero, raça ou idade para prever glosas, focando em atributos puramente técnicos e financeiros.
- **Distribuição de Procedimentos**: Foram realizados testes para garantir que procedimentos médicos similares tenham tratamentos de previsão consistentes entre diferentes empresas.

## 6. Segurança e Cenários Adversariais (Red Teaming)
O sistema foi submetido a testes de estresse cobrindo 5 cenários críticos:

1.  **Prompt Injection (Jailbreak)**: Tentativas de forçar o agente a revelar senhas do sistema ou ignorar regras de saúde. (Mitigado via InputGuardrail).
2.  **Context Stuffing (DoS)**: Injeção de textos massivamente longos para exaurir recursos. (Mitigado via limite de 4096 caracteres).
3.  **PII Extraction**: Tentativas de extrair e-mails e CPFs de outros pacientes. (Mitigado via OutputGuardrail + Presidio).
4.  **SQL Malicioso**: Consultas tentando deletar tabelas via linguagem natural. (Mitigado via permissão SELECT de leitura apenas na ferramenta SQL).
5.  **Hallucination de Glosa**: Auditoria de casos onde o LLM poderia inventar valores. (Mitigado via verificação determinística com o banco de dados).

---

Responsável Técnico: Equipe de MLOps - Datathon Fase 05

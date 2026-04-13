# OWASP Top 10 for LLM Applications — Mapeamento de Ameaças

Este documento descreve as principais ameaças de segurança identificadas para o sistema de Auditoria de Saúde (Ana) e as respectivas estratégias de mitigação implementadas, seguindo o padrão **OWASP Top 10 para Aplicações de LLM (2025)**.

| ID | Ameaça (OWASP) | Descrição do Risco | Mitigação Implementada / Planejada |
| :--- | :--- | :--- | :--- |
| **LLM01** | **Prompt Injection** | Usuário envia comandos para ignorar instruções e extrair segredos ou manipular a lógica de auditoria. | **InputGuardrail**: Uso de Regex para detectar padrões de injeção ("ignore previous instructions"). Bloqueio de inputs > 4096 caracteres. |
| **LLM02** | **Insecure Output Handling** | O output do LLM pode conter scripts maliciosos ou comandos SQL que seriam executados cegamente. | **Sanitização AST**: Cálculos matemáticos são processados via representação abstrata (AST), impedindo a execução de funções perigosas como `eval()`. |
| **LLM06** | **Sensitive Information Disclosure** | O modelo pode revelar dados sensíveis de saúde (PII) no output se não houver filtragem. | **OutputGuardrail + Presidio**: Uso do engine da Microsoft para detectar e anonimizar nomes, CPFs, emails e telefones em tempo real antes de exibir ao usuário. |
| **LLM08** | **Excessive Agency** | O agente pode executar ferramentas com permissões excessivas, alterando o banco de dados sem necessidade. | **Privilégios Mínimos**: As ferramentas SQL (`search_reimbursement_data`) possuem acesso apenas para leitura (SELECT) e filtros estritos baseados no contexto da query. |
| **LLM09** | **Overreliance** | O auditor pode aceitar cegamente uma previsão de glosa da IA sem verificar os dados originais. | **Hibridismo Determinístico**: O agente é obrigado a retornar os dados brutos do `db_lite` no pensamento, permitindo a verificação cruzada humana na resposta final. |

---

## Detalhes das Mitigações em Operação

### 1. Guardrails de Segurança (Camada 1)
A implementação em `src/security/guardrails.py` atua como um firewall bidirecional:
- **Entrada**: Filtra tentativas de *jailbreak* e *system prompt leak*.
- **Saída**: Escaneia resultados em busca de dados sensíveis antes que eles toquem o front-end.

### 2. Sandbox de Execução (Camada 2)
Todas as operações de agregação e cálculos de glosas previstos são realizados em um ambiente que não permite execução de código Python arbitrário, mitigando vetores de ataque via injeção SQL no LLM.

### 3. Soberania de Dados
Ao utilizar o **LiteLlama-460M localmente**, o risco de vazamento de dados para terceiros (Azure, OpenAI, Anthropic) é eliminado, reduzindo drasticamente o blast radius de ataques de fornecedores.

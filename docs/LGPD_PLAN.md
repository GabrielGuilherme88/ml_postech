# Plano de Conformidade LGPD — Auditoria de Saúde (Ana)

Este documento detalha as medidas técnicas e organizacionais adotadas para garantir a proteção de dados pessoais e sensíveis no sistema de auditoria de glosas, em conformidade com a **Lei Geral de Proteção de Dados (Lei nº 13.709/2018)**.

## 1. Classificação e Inventário de Dados
O sistema processa dados de transações de reembolso médico que incluem:
- **Dados Pessoais**: Nomes de beneficiários, endereços de e-mail.
- **Dados Pessoais Sensíveis**: Informações de saúde (procedimentos, exames, glosas médicas).

## 2. Princípios de Proteção Aplicados

### 2.1. Privacy-by-Design: Execução Local
Diferente de sistemas baseados em nuvem pública (SaaS), todo o processamento dos dados ocorre no servidor controlado pelo controlador (empresa):
- **Modelo de Linguagem**: LiteLlama-460M é executado localmente. Nenhum dado de saúde é enviado para APIs externas.
- **Banco de Dados**: SQLite local (`db_lite`) sem acesso externo.

### 2.2. Minimização de Dados
As ferramentas do agente e os scripts de treinamento acessam apenas as colunas estritamente necessárias para a previsão de glosas (`vl_informado`, `cd_procedimento`, `qt_informado`). Identificadores diretos como nomes de pacientes são excluídos da inferência do modelo ML.

### 2.3. Anonimização e Pseudonimização
O sistema utiliza o **Microsoft Presidio** integrado ao `OutputGuardrail` para atuar em tempo real:
- **Detecção**: O engine identifica entidades como `PERSON`, `EMAIL`, `BR_CPF` e `PHONE_NUMBER`.
- **Substituição**: Aplica técnicas de ocultação, substituindo dados reais por marcadores genéricos (ex: `[PERSON_1]`), garantindo que a resposta final do agente não exponha dados sensíveis desnecessariamente.

## 3. Direitos do Titular
O sistema armazena logs de auditoria no MLflow e banco de dados, permitindo:
- **Acesso e Portabilidade**: Os dados podem ser extraídos e revisados via scripts de gestão do banco.
- **Exclusão**: Suporte para deleção via solicitações manuais nas tabelas `pedidos_reembolso` e `db_model`.

## 4. Segurança da Informação
- **Controle de Acessos**: Restrição a nível de aplicação e infraestrutura.
- **Criptografia**: Recomendação de uso de volumes criptografados para o banco `db_lite` e artefatos DVC em produção.

---

### Responsável pelo Tratamento
*   **Controlador**: [Grupo-XX / Instituição Financeira]
*   **Operador**: Agente de IA "Ana" (Sistema Local)

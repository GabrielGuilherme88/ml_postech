# Checklist de Entrega Final - Datathon Fase 05

Use este checklist como guia de progresso antes do Demo Day. Você pode editá-lo e marcar os itens conforme for finalizando.

### Etapa 1 — Dados + Baseline
- [ ] EDA documentada com insights relevantes para o problema da empresa.
- [ ] Baseline treinado e métricas reportadas no MLflow.
- [ ] Pipeline versionado (DVC + Docker) e reprodutível.
- [ ] Métricas de negócio mapeadas para métricas técnicas.
- [ ] `pyproject.toml` com todas as dependências.

### Etapa 2 — LLM + Agente
- [ ] LLM servido via API com quantização aplicada.
- [ ] Agente ReAct funcional com ≥ 3 tools relevantes ao domínio.
- [ ] RAG retornando contexto relevante dos dados fornecidos.
- [ ] CI/CD pipeline funcional (GitHub Actions).
- [ ] Benchmark documentado com ≥ 3 configurações.

### Etapa 3 — Avaliação + Observabilidade
- [ ] Golden set com ≥ 20 pares relevantes ao domínio.
- [ ] RAGAS: 4 métricas calculadas e reportadas.
- [ ] LLM-as-judge com ≥ 3 critérios (incluindo critério de negócio).
- [ ] Telemetria e dashboard funcionando end-to-end.
- [ ] Detecção de drift implementada e documentada.

### Etapa 4 — Segurança + Governança
- [ ] OWASP mapping com ≥ 5 ameaças e mitigações.
- [ ] Guardrails de input e output funcionais.
- [ ] ≥ 5 cenários adversariais testados e documentados.
- [ ] Plano LGPD aplicado ao caso real.
- [ ] Explicabilidade e fairness documentados.
- [ ] System Card completo.

### Demo Day
- [ ] Pitch ≤ 10 min: Problema → Abordagem → Demo → Resultados → Impacto.
- [ ] Ensaio prévio com timer.
- [ ] Backup: slides offline caso a demo falhe.
- [ ] Preparação para Q&A técnico e de negócio.

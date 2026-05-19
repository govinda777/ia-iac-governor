# 📋 BACKLOG: IA-IaC Governor

**Status do Produto:** Fase de consolidação do MVP (Minimum Viable Product).
**Objetivo da Próxima Release:** Execução do fluxo de ponta a ponta (E2E) do Framework de Segurança de Infraestrutura com tratamento de erros robusto. O foco principal é validar nossa engine de análise preditiva de risco rodando exemplos e benchmarks na CI, e utilizar IA (LLM) como motor preditivo para detectar combinações tóxicas complexas de infraestrutura.

---

## 🏗️ Infra & Core Engine

- [ ] **Estabilizar Integração E2E com Emulador Floci**
  - Executar o ciclo completo de governança (`terraform init/plan/apply`) confiavelmente contra os endpoints locais do emulador Floci.
  - *Critério de Aceite:* Script `test_examples.py` finalizando em sucesso absoluto na pipeline de CI sem falsos positivos relacionados a latência ou conectividade.
- [ ] **Maturidade e Congelamento de Escopo do Custom Provider AWS (`governor`)**
  - Restringir a atuação do provider em Go aos componentes estruturais base (VPC, Subnet, IAM, SG). Novos recursos deverão seguir a arquitetura de "Black Box" via Módulos Terraform.
  - *Critério de Aceite:* Não existem novos recursos da AWS implementados nativamente em Go no provedor; módulos delegados documentados em `golden_paths`.
- [ ] **Implementação do Custom Provider para Helm (Kubernetes)**
  - Estruturar a fundação de um novo custom provider para orquestração focada em Kubernetes (Helm), priorizando captura agressiva de metadados.
  - *Critério de Aceite:* Suporte e testes unitários garantindo que os dados de telemetria dos deploys alimentem com sucesso o contexto da base preditiva.
- [ ] **Otimização do Parser HCL de Fallback e Cache**
  - Fortalecer o parser mock customizado para geração de `resource_changes` caso o binário Terraform falhe, garantindo performance pelo cache de `golden_paths/provider.tf`.
  - *Critério de Aceite:* Parser robusto contra blocos complexos no HCL; cobertura de testes em edge cases atingindo >90%.

## 🖥️ Frontend & UX

- [ ] **Renderização de Dados Preditivos e Drift em Tempo Real**
  - Ajustar o SPA (`index.html`) para orquestrar gráficos instanciados em `Chart.js` via `requestAnimationFrame`.
  - *Critério de Aceite:* Transições DOM limpas, redimensionamento fluido de componentes visuais, sem memory leaks nem cintilação.
- [ ] **Componente de Visualização de Remediações (Patch Diffing)**
  - Adicionar suporte na UI para renderizar de forma nativa e comparativa os diffs HCL e as sugestões de remediação recomendadas pelos agentes preditivos.
  - *Critério de Aceite:* View estilo "split-pane" com highlighting de syntax para original vs patch.

## 🔒 Segurança & Resiliência

- [ ] **Refatoração Modular dos Bundles OPA/Rego (`policies/compliance.rego`)**
  - Desacoplar políticas grandes, categorizando-as por framework de compliance e separando regras Hard (Block) de Soft (Warn).
  - *Critério de Aceite:* Motor OPA consegue avaliar os planos JSON complexos de benchmarks com tempo de resposta inferior a 2 segundos em `opa exec`.
- [ ] **Evolução do Digital Twin (Security Graph) para Detecção Lateral**
  - Incrementar o `schema/security_graph.json` adicionando novas arestas para correlacionar riscos híbridos entre Rede e Identidade (ex: `CAN_ASSUME_ROLE_IN_VPC`).
  - *Critério de Aceite:* Mapeamento de grafo identifica as pontes tóxicas públicas/privadas contidas no escopo `/benchmarks` corretamente.

## 📈 Monitoramento & Analytics

- [ ] **Integração Dinâmica de LLM Avançada (Análise Preditiva)**
  - Consolidar agentes autônomos (Arquiteto, Auditor) via CrewAI para atuar na pipeline na presença de credenciais (ex: `GEMINI_API_KEY`), correlacionando contexto extra além do estático.
  - *Critério de Aceite:* O motor emite predições logadas que não foram mapeadas de forma direta nas policies OPA.
- [ ] **Retrospectiva Contínua e Auto-Fortificação**
  - Implementar um loop no qual as falhas e sucessos de validação alimentam a IA, induzindo análises críticas sobre os próprios controles vigentes.
  - *Critério de Aceite:* O sistema deve registrar internamente lacunas em políticas observadas na retrospectiva.
- [ ] **Geração Autônoma de Self-Improvement PRs**
  - Habilitar capacidade dos agentes elaborarem PRs adicionando novas regras Rego ou proteções em caso de descoberta de gaps heurísticos.
  - *Critério de Aceite:* Patches/PRs submetidos geram logs coerentes e testes próprios sem quebrar CI (Auto-Fortificação funcional).

---

## 🚦 Pontos Cegos & Edge Cases

- [ ] **Tratamento de Rate Limits e Timeouts da LLM (Circuit Breaker)**
  - **Risco:** Gargalos nas chamadas LLM e APIs externas travando as pipelines de CI/CD.
  - **Ação:** Integrar um mecanismo de *Circuit Breaker* que realize failover silencioso ("graceful degradation") e retorne estritamente à análise OPA + Grafo em caso de timeout.
- [ ] **Prevenção Estrita de Injeção de HCL e Payload Envenenado**
  - **Risco:** Outputs de remediação propostos pela LLM podem possuir sintaxe perigosa ou injetar configurações tóxicas acidentalmente.
  - **Ação:** Fazer sanitização estrita do JSON gerado, utilizando parser nativo, proibindo `eval`, e validando todo patch proposto contra as políticas de OPA de proteção de integridade.
- [ ] **Isolamento de State em Testes Paralelos (Race Conditions)**
  - **Risco:** Corrupção de arquivos `.terraform` ao invocar a `GovernanceManagerTool` em CI rodando múltiplos exemplos simulados ao mesmo tempo.
  - **Ação:** Instanciar execução do Terraform init/plan dentro de diretórios temporários (`tempfile.mkdtemp`) replicando mocks de pastas.
- [ ] **Vazamento e Mascaramento de Segredos de IA**
  - **Risco:** Chaves como `GEMINI_API_KEY` serem injetadas no SPA ou acidentalmente vazadas nos logs de diff da infraestrutura.
  - **Ação:** Filtragem implacável de segredos utilizando regex no pipeline de exportação dos logs e no parser do frontend.

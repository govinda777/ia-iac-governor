# 📋 BACKLOG: IA-IaC Governor

**Status do Produto:** Fase de consolidação do MVP (Minimum Viable Product).
**Objetivo da Próxima Release:** Execução do fluxo de ponta a ponta (E2E) do Framework de Segurança de Infraestrutura com tratamento de erros robusto. O foco principal é validar nossa engine de análise preditiva de risco rodando exemplos e benchmarks na CI, e utilizar IA (LLM) como motor preditivo desacoplado para detectar combinações tóxicas complexas de infraestrutura, garantindo resiliência em falhas de execução.

---

## 🏗️ Infra & Core Engine

- [ ] **Estabilizar Integração E2E com Emulador Floci**
  - **Descrição Técnica:** Garantir execução confiável do ciclo de governança (`terraform init/plan/apply`) contra endpoints locais do Floci (AWS Emulator). Eliminar problemas de resolução de rede e delays do container em pipeline.
  - **Critério de Aceite:** Script `test_examples.py` finalizando com sucesso absoluto na CI, validando exemplos locais contra o emulador de forma robusta e paralelizável (utilizando diretórios temporários na `GovernanceManagerTool`).
- [ ] **Maturidade e Congelamento de Escopo do Custom Provider AWS (`governor`)**
  - **Descrição Técnica:** Manter foco arquitetural em "Black Box" para recursos gerenciados (VPC, Subnet, IAM, SG). Integrar a validação human-in-the-loop (via sistema de ticket) nativamente na avaliação de `governor_managed_security_group`.
  - **Critério de Aceite:** Módulos Terraform (`golden_paths`) consolidados; pipeline interrompe corretamente execução no aguardo do ticket de aprovação em mudanças de Security Groups e retoma com status 'APPROVED'.
- [ ] **Fundação do Custom Provider para Kubernetes (Helm)**
  - **Descrição Técnica:** Estruturar um provider piloto para Helm com objetivo primário de capturar telemetria e metadados agressivamente durante deploys em clusters.
  - **Critério de Aceite:** Código inicial em Go estabelecido; testes unitários comprovam a extração correta dos metadados de configuração de rede (NetworkPolicies/Ingress).
- [ ] **Otimização de Performance do Parser HCL (Fallback) e Sistema de Cache**
  - **Descrição Técnica:** Refinar o parser regex-based em `GovernanceManagerTool` e garantir estabilidade do `_PROVIDER_TEMPLATE_CACHE` para contornar falhas de `terraform init` (ex: locks corrompidos na CI).
  - **Critério de Aceite:** Conversão de raw HCL para mock `resource_changes` executada sem overhead de I/O em menos de 1 segundo para benchmarks massivos, mesmo quando sem acesso a internet ou provedores locais.

## 🖥️ Frontend & UX

- [ ] **Refatoração Visual de Gráficos Preditivos no SPA (`index.html`)**
  - **Descrição Técnica:** Consertar possíveis bugs de renderização no carregamento dinâmico de documentação (marked.js) atrelado aos gráficos `Chart.js` (`cognitive` e `drift`).
  - **Critério de Aceite:** Gráficos redimensionam adequadamente e atualizam valores via callbacks encapsulados em `requestAnimationFrame` na função `navigate()`, prevenindo problemas de reflow no DOM.
- [ ] **Visualizador de Diffs e Remediação (Split-Pane)**
  - **Descrição Técnica:** Implementar componente de UI que renderiza diffs (Merge/Patch Diff) destacando a sugestão de correção HCL gerada pelo AI Reasoner.
  - **Critério de Aceite:** Componente de fácil leitura comparativa ("original vs sugestão") adaptado com `@tailwindcss/typography` no painel principal da SPA.

## 🔒 Segurança & Resiliência

- [ ] **Governança Determinística de Estado (OPA Hard Policies)**
  - **Descrição Técnica:** Expandir e modularizar `policies/compliance.rego` para bloqueios estritos (Hard Policies). Validar associação de recursos internos (ex: `governor_managed_subnet` tier "private") com acessos públicos (ex: `aws_internet_gateway`).
  - **Critério de Aceite:** OPA deve barrar de forma síncrona o deploy no CI e disparar evento para log de auditoria, antes de qualquer LLM ser invocada.
- [ ] **Evolução do Security Graph (Detecção de Ligações Tóxicas)**
  - **Descrição Técnica:** Aprimorar o `GraphProvider` (`core/governance/providers/graph_provider.py`) para ler o manifesto `schema/security_graph.json` e construir rotas laterais de ataque predatórias (Cross-resource audit).
  - **Critério de Aceite:** Motor detecta corretamente bypasses de políticas estáticas e identifica padrões tóxicos (ex: EC2 com Role de KMS + IP Público) analisando dependências no plano (JSON).

## 📈 Monitoramento & Analytics

- [ ] **Orquestração Assíncrona do LLM para Remediação (AI Reasoner)**
  - **Descrição Técnica:** Integrar chamadas LLM de forma puramente assíncrona. O Agente (Arquiteto/Auditor via CrewAI) não deve bloquear a CI; atua apenas para prover sugestões de refatoração do código quando regras determinísticas falham.
  - **Critério de Aceite:** A engine OPA emite um DENY, liberando a pipeline imediatamente com status de erro, e a LLM dispara um job separado que apenas comenta as remediações no pull request.
- [ ] **Gestão Segura de Self-Improvement Pull Requests**
  - **Descrição Técnica:** Criar rotina na qual a IA pode propor melhorias para as políticas (OPA ou Grafo) em caso de drift.
  - **Critério de Aceite:** Todo Pull Request gerado pela IA **exige estritamente** revisão manual (Human-in-the-loop). Bloqueios contra auto-merge ativados no repositório.

---

## 🚦 Pontos Cegos & Edge Cases

- [ ] **Tratamento de Rate Limits e Degradação Graciosa (LLM)**
  - **Risco:** CI travada por limite de quota na API (Gemini/OpenAI) ou timeout de rede em ambientes isolados.
  - **Ação:** Implementar padrão *Circuit Breaker*. Se a chamada para LLM demorar ou falhar, o sistema reverte nativamente para OPA estrito (Graceful Degradation) sem penalizar a runtime do CI.
- [ ] **Sandboxing de Segurança em Testes E2E Paralelos (Race Conditions)**
  - **Risco:** Execuções múltiplas simultâneas de instâncias do Terraform (`.terraform` state collision) no GitHub Actions quebram os cenários e corrompem os planos locais de testes.
  - **Ação:** Isolar a execução da `GovernanceManagerTool` em CI. Copiar dinamicamente arquivos locais, como `golden_paths`, para diretórios temporários no sistema do host rodando o script antes de invocar `terraform init/plan`.
- [ ] **Filtragem e Sanitização Estrita de Saídas do LLM (Injection Protection)**
  - **Risco:** Agentes podem alucinar sintaxes em HCL perigosas (ex: injetando chaves sensíveis) ou utilizar comandos shell nas sugestões.
  - **Ação:** O JSON de resposta da LLM deve passar por uma sanitização nativa, garantindo que o Output contenha apenas blocos válidos de HCL sem interpolações sensíveis ou funções como `eval`. Validar o patch no OPA antes de expor no Pull Request.
- [ ] **Redundância de Verificação de Frontend sem Internet**
  - **Risco:** Em testes E2E e builds executados em redes corporativas com bloqueios, scripts do Playwright para testes no UI não vão resolver os scripts CDN (ex: Tailwind, marked.js).
  - **Ação:** Configurar scripts do Playwright para utilizar os eventos de `domcontentloaded` ou `commit` e iniciar com `python3 -m http.server 8000 &`, garantindo a assertividade visual independentemente do timeout `networkidle`.

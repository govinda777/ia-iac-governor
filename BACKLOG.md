# 📋 BACKLOG: IA-IaC Governor

**Status do Produto:** Fase de consolidação do MVP (Minimum Viable Product).
**Objetivo da Próxima Release:** Execução do fluxo E2E (End-to-End) com governança estática rigorosa na CI (SLA < 10s), análise semântica assíncrona baseada em Grafos via PR (com IA local para geração de patch), testes automatizados contra o emulador Floci, e expansão controlada do provedor customizado.

---

## 🏗️ Épico 1: Infraestrutura, Core Engine & Custom Provider
*Foco na resiliência do provider Go, testes com Floci e orquestração base do Terraform.*

- [ ] **Estabilizar Integração E2E com Floci:** Garantir que o ciclo completo (`terraform init/plan/apply`) com o provider `governor` execute confiavelmente contra os endpoints do emulador Floci no ambiente local e CI. *Critério de Aceite: `test_examples.py` rodando sem falsos positivos de rede.*
- [ ] **Otimização de Cache e I/O no Plan Evaluation:** Implementar cacheamento avançado do JSON do Terraform Plan no `GovernanceManagerTool` e otimizar tempo de execução na CI para garantir SLA de < 10 segundos.
- [ ] **Expansão Estratégica do Custom Provider:** Implementar gerenciamento de um novo recurso seguro (ex: `governor_managed_s3_bucket`) seguindo o padrão "Black Box" (desenvolvedor passa Intent, provider computa ARN/detalhes e injeta políticas restritivas).
- [ ] **Melhoria do Parser HCL de Fallback:** Aprimorar o fallback customizado (mock `resource_changes`) quando o `terraform init` falhar na CI por bloqueio de rede, garantindo extração robusta de atributos críticos para avaliação do OPA.

## ⚖️ Épico 2: Motor OPA & Governança Estática (Gating CI)
*Foco em Hard Policies determinísticas rápidas que operam bloqueando a esteira.*

- [ ] **Refatoração dos Bundles Rego (`policies/compliance.rego`):** Estruturar políticas por família de compliance (ex: NIST, CIS) de forma modular. *Critério de Aceite: CI capaz de rodar validações com `opa exec` em tempo inferior a 2 segundos.*
- [ ] **Strict Block para Missing Tags:** Garantir que o OPA rejeite planos que não contenham as tags obrigatórias (`CostCenter`, `Project`) em recursos base, abortando a esteira IMEDIATAMENTE com código de erro correspondente.
- [ ] **Integração de Relatórios no CI/CD:** Fazer com que as respostas do OPA sejam formatadas e renderizadas como anotações na interface do GitHub Actions / GitLab CI, com links para a documentação de correção.

## 🧠 Épico 3: Motor Semântico & Grafo de Segurança (Async PR Bot & IA Local)
*Foco na readequação arquitetural: A LLM não bloqueia o CI; a LLM será executada **localmente** para atuar como revisora e explicar o contexto do Grafo, gerando sugestões de código no PR.*

- [ ] **Desacoplamento LLM da Esteira CI:** Extrair chamadas à API LiteLLM/CrewAI do caminho crítico do CI (pipeline principal). A esteira deve consultar *apenas* o Security Graph (determinístico) ou OPA para bloquear o deploy. A execução da LLM ficará restrita aos ambientes locais e chamadas assíncronas de bot.
- [ ] **Redefinição do Papel da LLM (Explanation & Patch Generation):** Utilizar a LLM estritamente como um *Async PR Revisor* rodando localmente/fora de banda. *Critério de Aceite: Após um alerta gerado pelo motor determinístico/Grafo, a LLM é acionada localmente para analisar o erro e sugerir um patch HCL no Pull Request.*
- [ ] **Evolução do Schema do Security Graph (`schema/security_graph.json`):** Mapear novos tipos de arestas (edges) para correlacionar problemas de Rede com Identidade (ex: `CAN_ASSUME_ROLE_IN_VPC`).
- [ ] **Framework de Benchmarks (Cross-Account Vulnerabilities):** Ampliar cenários do diretório `/benchmarks` para comprovar que as queries no Grafo detectam pontes tóxicas entre público e privado sem falsos negativos.

## 🖥️ Épico 4: Plataforma SPA & Documentação
*Foco na interface de consumo dos relatórios via `index.html` e usabilidade de onboarding.*

- [ ] **Renderização de Dados de Drift em Tempo Real:** Conectar os relatórios gerados pelo motor (ex: via JSON dumps) ao frontend, garantindo que gráficos de risco (Chart.js) sejam desenhados corretamente através de `requestAnimationFrame`.
- [ ] **Componente de Visualização de Remediações:** Adicionar suporte na SPA para exibir de forma intuitiva os diffs / patches gerados sugeridos para auto-remediação.

## 🔒 Pontos Cegos & Edge Cases (Resiliência Operacional)
*Tarefas focadas na estabilidade e segurança "by design" do sistema.*

- [ ] **Tratamento de Rate Limits e Timeouts da LLM:** O job assíncrono/local que gera comentários de PR DEVE possuir mecanismo de "Circuit Breaker" e "Exponential Backoff", falhando graciosamente (exibindo apenas o alerta seco do Grafo) caso a API da LLM (OpenAI/Anthropic/etc) fique inoperante.
- [ ] **Prevenção contra Injeção de Código (HCL Injection):** Sanitizar rigidamente o output gerado pela LLM antes de enviá-lo como sugestão de código no GitHub/GitLab, prevenindo injeções acidentais ou prompts maliciosos inseridos no HCL.
- [ ] **State Integrity & Race Conditions em Testes:** Garantir que o "ticket de aprovação" simulado no estado do `governor_managed_security_group` não sofra corrupção quando processos paralelos rodarem a suíte de testes contra os emuladores em Go/Floci.
- [ ] **Fallback de Segurança (Fail-Safe):** Se o parser HCL interno (fallback) falhar ou o plano Terraform submetido vier vazio, o sistema deve falhar de forma fechada (Deny by Default) e não gerar uma "Aprovação Silenciosa".

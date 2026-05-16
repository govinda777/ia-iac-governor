# 📋 BACKLOG: IA-IaC Governor

**Status do Produto:** Fase de consolidação do MVP (Minimum Viable Product).
**Objetivo da Próxima Release:** Execução do fluxo E2E (End-to-End) do nosso **Framework de Segurança de Infraestrutura**. O foco principal é validar a nossa engine de **análise preditiva de risco** rodando os exemplos e benchmarks na CI. A LLM, quando configurada (`GEMINI_API_KEY` ou similar), deve atuar como um motor preditivo avançado que amplia a capacidade do framework de detectar combinações tóxicas complexas.

---

## 🏗️ Épico 1: Core Engine do Framework & Custom Providers
*Foco na resiliência dos provedores (AWS e Kubernetes) e testes da suíte E2E.*

- [ ] **Estabilizar Integração E2E com Floci:** Garantir que o ciclo completo de validação do framework (`terraform init/plan/apply`) execute confiavelmente contra os endpoints do emulador Floci para validar nossos exemplos. *Critério de Aceite: `test_examples.py` rodando na pipeline sem falsos positivos de rede.*
- [ ] **Maturidade e Restrição de Escopo do Custom Provider AWS (`governor`):** Focar exclusivamente na estabilidade dos componentes estruturais base (VPC, Subnet, IAM, SG) do nosso custom provider. É expressamente definido que **não haverá implementação de novos recursos no provedor AWS em Go**. Outros recursos necessários deverão ser implementados através de **Módulos Customizados (Terraform Modules)** seguindo o padrão "Black Box".
- [ ] **Implementação do Custom Provider para Helm:** Iniciar o desenvolvimento de um novo Custom Provider focado em orquestração Kubernetes (Helm). Este provider deve ser construído garantindo a coleta intensiva de **todos os dados de uso e telemetria**. Essa rastreabilidade é fundamental para alimentar a nossa engine preditiva com contexto sobre os artefatos implantados nos clusters.
- [ ] **Otimização do Parser HCL de Fallback:** Aprimorar o fallback customizado (mock `resource_changes`) para extração robusta de atributos críticos em avaliações preditivas. Lembrando que, por padrão, os exemplos são executados apontando para o Emulador Floci; caso um exemplo específico precise rodar contra a AWS real, isso deve estar explicitamente configurado no bloco do provider do respectivo teste.

## ⚖️ Épico 2: Motor Determinístico OPA & Validação de Exemplos
*Foco na análise estática rápida que compõe a primeira barreira do nosso framework de governança.*

- [ ] **Refatoração dos Bundles Rego (`policies/compliance.rego`):** Estruturar políticas por família de compliance (ex: NIST, CIS) de forma modular para validar os exemplos mais rápido. *Critério de Aceite: Pipeline do framework deve ser capaz de validar os exemplos de HCL com `opa exec` em tempo inferior a 2 segundos.*

## 🧠 Épico 3: Motor Preditivo, Retrospectiva Contínua e Auto-Fortificação
*Foco no nosso diferencial: A análise preditiva que evolui e fortifica o próprio framework baseada em inteligência retroativa.*

- [ ] **Integração Dinâmica da LLM para Análise Preditiva Profunda:** Configurar a engine para que, quando uma chave de IA (ex: `GEMINI_API_KEY`) for detectada na pipeline ou ambiente local, o framework acione a IA para realizar predições complexas baseadas no Grafo, e não apenas regras estáticas.
- [ ] **Retrospectiva Contínua e Auto-Fortificação do Framework:** Como ainda precisamos comprovar eficiência na detecção de falhas latentes, o agente preditivo deve se beneficiar do próprio ciclo de validação. A cada análise concluída de infraestrutura (nos exemplos/benchmarks), o agente deve rodar um loop de "retrospectiva" para identificar lacunas no processo atual de checagem.
- [ ] **Geração Autônoma de PRs de Melhoria (Self-Improvement):** Quando o agente preditivo identificar que a fortificação do framework precisa evoluir, ele deve ser capaz de **criar e submeter Pull Requests automáticos no repositório do próprio projeto**, adicionando novas políticas Rego ou controles otimizados, garantindo que o framework se torne mais blindado a cada iteração.
- [ ] **Evolução do Schema do Security Graph (`schema/security_graph.json`):** Mapear novos tipos de arestas (edges) para correlacionar problemas latentes de Rede com Identidade (ex: identificar proativamente um `CAN_ASSUME_ROLE_IN_VPC` antes do deploy).
- [ ] **Framework de Benchmarks (Cross-Account Vulnerabilities):** Criar e rodar testes automatizados na pipeline validando cenários preditivos do diretório `/benchmarks` (ex: prever pontes tóxicas entre redes públicas e privadas usando correlação de dados).

## 🖥️ Épico 4: Plataforma SPA & Documentação
*Foco na interface de consumo dos relatórios via `index.html` e usabilidade do framework.*

- [ ] **Renderização de Dados Preditivos e Drift em Tempo Real:** Conectar os relatórios gerados pelo framework ao frontend, garantindo que gráficos de risco (Chart.js) sejam desenhados corretamente através de `requestAnimationFrame`.
- [ ] **Componente de Visualização de Remediações:** Adicionar suporte na SPA para exibir de forma intuitiva os diffs / patches gerados que corrigem vulnerabilidades preditas.

## 🔒 Pontos Cegos & Edge Cases (Resiliência Operacional)
*Tarefas focadas na estabilidade e segurança "by design" do próprio framework.*

- [ ] **Tratamento de Rate Limits e Timeouts da LLM:** O acionamento da análise preditiva avançada via IA DEVE possuir mecanismo de "Circuit Breaker". Caso a API (ex: Gemini) falhe, o framework deve falhar graciosamente e reverter (fallback) para a análise baseada apenas nas queries determinísticas do Grafo e OPA.
- [ ] **Prevenção contra Injeção de Código (HCL Injection):** Sanitizar rigidamente o output preditivo gerado pela LLM antes de exibi-lo como sugestão de código (patch) ou ao criar auto-PRs, prevenindo injeções acidentais baseadas em HCL comprometido.
- [ ] **State Integrity & Race Conditions em Testes:** Garantir que recursos simulados (como o estado do `governor_managed_security_group`) não sofram corrupção quando processos paralelos da pipeline rodarem os exemplos contra os emuladores.
- [ ] **Fallback de Segurança (Fail-Safe):** Se o parser HCL interno falhar no meio de uma predição complexa, o framework deve adotar a política "Deny by Default" nas análises de risco.

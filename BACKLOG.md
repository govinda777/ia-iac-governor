# 📋 BACKLOG: IA-IaC Governor

**Status do Produto:** Fase de consolidação do MVP (Minimum Viable Product).
**Objetivo da Próxima Release:** Executar o fluxo E2E (End-to-End) do nosso Framework de Segurança de Infraestrutura. O foco principal é consolidar os portões de segurança sequenciais: iniciando com análises determinísticas (OPA + Grafos) e finalizando com análises semânticas profundas via LLM.

---

## 🏗️ Infra & Core Engine
*Foco na resiliência dos provedores (AWS e Kubernetes) e consolidação da suíte E2E.*

- [ ] **Estabilizar Integração E2E com Floci:** Garantir que o ciclo completo (`terraform init/plan/apply`) execute de forma confiável contra os endpoints do emulador Floci.
  - *Critério de Aceite:* O script `test_examples.py` roda na pipeline de CI em paralelo, sem falsos positivos de rede ou colisões de `.terraform` state (usando diretórios temporários isolados).
- [ ] **Maturidade e Restrição de Escopo do Custom Provider AWS (`governor`):** O provedor Go focará estritamente na gestão de recursos core (VPC, Subnet, IAM, SG).
  - *Critério de Aceite:* Sem adição de features fora do core em Go. Recursos adicionais devem seguir o padrão "Black Box" encapsulados em módulos Terraform (`golden_paths/`).
- [ ] **Spike Técnico para o Helm Custom Provider:** Iniciar a arquitetura do provider para Kubernetes.
  - *Critério de Aceite:* Documento técnico definindo o stack agnóstico que será utilizado para coletar telemetria e rastreabilidade dos artefatos no K8s, servindo de base para o Grafo de Segurança sem acoplamento precoce a fornecedores específicos.
- [ ] **Otimização do Parser HCL de Fallback:** Refatorar o fallback regex do `GovernanceManagerTool` para situações onde o `terraform plan` falha na CI devido a problemas em dependências de ambiente.
  - *Critério de Aceite:* O fallback gera mocks `resource_changes` de forma determinística, permitindo validação das policies OPA sem mascarar infraestrutura insegura.

## 🔒 Segurança & Resiliência
*Foco nos portões de segurança e fortificação contínua do framework.*

- [ ] **Refatoração dos Bundles Rego (Portão 1 - OPA):** Modularizar `policies/compliance.rego` para categorizar regras base (NIST, CIS, etc).
  - *Critério de Aceite:* As validações de `tfplan` contra as regras do OPA são instantâneas, barrando problemas como IPs públicos e configurações inseguras imediatamente.
- [ ] **Evolução do Security Graph (Portão 2 - Grafo Determinístico):** Mapear novas arestas no `schema/security_graph.json` para detectar complexidade topológica.
  - *Critério de Aceite:* A plataforma identifica e bloqueia vetores de ataque cruzados documentados em `/benchmarks` (ex: Public-Private Bridge) baseada exclusivamente em sua correlação matemática.
- [ ] **Integração Dinâmica da LLM (Portão 3 - Análise Semântica Preditiva):** Após validação OPA e Grafo, engajar o raciocínio semântico avançado da LLM para inferências de negócios sobre a arquitetura.
  - *Critério de Aceite:* A IA atua na validação de intenção e gera propostas de remedição HCL. Falhas na API da IA (timeouts) disparam alertas, mas não quebram os vereditos já consolidados pelos portões estáticos (OPA/Grafo).
- [ ] **Geração Autônoma de PRs de Melhoria (Self-Improvement):** O agente preditivo deve sugerir proativamente novas políticas (Rego) se detectar gaps no framework base após analisar um cluster vulnerável.
  - *Critério de Aceite:* A IA abre Pull Requests no repositório. O processo **exige obrigatoriamente aprovação humana** no Code Review antes de realizar o merge no motor OPA.

## 🖥️ Frontend & UX
*Foco na interface de consumo e usabilidade via `index.html`.*

- [ ] **Renderização de Dados e Relatórios de Risco:** Exibição robusta do estado da topologia da nuvem.
  - *Critério de Aceite:* Componentes do Chart.js são criados/atualizados rigorosamente dentro de chamadas `requestAnimationFrame` para evitar dessincronia na renderização durante a navegação.
- [ ] **Visualizador de Diffs e Patches de Auto-Correção:** Interface dedicada para os desenvolvedores revisarem o código proposto pela camada semântica.
  - *Critério de Aceite:* Patches de correção do Terraform são apresentados em split-view (diff) com suporte a highlight da sintaxe HCL.

## 📈 Monitoramento & Analytics
*Métricas e telemetria interna do framework.*

- [ ] **Auditoria e Rastreabilidade de Decisões:** Armazenar todos os relatórios e decisões tomadas pelas diferentes camadas (OPA, Grafo e IA).
  - *Critério de Aceite:* Os eventos de aprovação ou rejeição de um CI/CD recebem um `correlation_id`, facilitando respostas a auditorias de compliance (SOC 2).
- [ ] **Guardrails Financeiros (Cost Provider):** Identificar variações financeiras bruscas no plano.
  - *Critério de Aceite:* Recursos cloud propostos têm tag de custo aferida e são valorados contra o motor de custos base (ex: instâncias maiores que m5.4xlarge alertam alto custo projetado).

---

## 🕳️ Pontos Cegos & Edge Cases (Resiliência Operacional)
*Tarefas direcionadas a tratamento de falhas, infraestrutura segura por design e limitações arquiteturais.*

- [ ] **Prevenção contra Vazamento de Segredos na IA:** O `tfplan` gerado pode conter senhas no provisionamento (RDS, credenciais temporárias). É obrigatório implementar um *scrubber* regex antes do envio do payload para a LLM, garantindo data privacy.
- [ ] **Mitigação de HCL Injection no Output da LLM:** O output preditivo gerado pela IA (em PRs ou patches) precisa passar por um parser de sintaxe e validação restrita, evitando que sugestões da IA injetem blocos mal-formatados ou comandos maliciosos no backend.
- [ ] **Resiliência e Circuit Breaker para LLMs:** Redes externas falham. É necessário estipular políticas de retentativas. Em caso de *timeout* persistente da LLM no Portão 3, o CI não deve travar o deploy se os portões críticos 1 (OPA) e 2 (Grafo) estiverem "Verdes" e de acordo com o threshold aceito para o projeto.
- [ ] **Integridade de Estado em Execuções Paralelas no CI:** Ferramentas rodando o `GovernanceManagerTool` em cenários concorrentes (vários PRs) podem corromper pastas `.terraform` se utilizarem o mesmo diretório. Deve-se reforçar a utilização exclusiva de diretórios temporários na execução isolada.
- [ ] **Validação Estrita do Mock Preditivo HCL:** A regex customizada do fallback de IaC pode sofrer bypass acidental em certas sintaxes obscuras de HCL, aprovando uma policy por ausência do field. Um mecanismo de *Deny by Default* em parseamentos incompletos precisa ser ativado para evitar "Falsos Negativos" críticos.

# Avaliação de Refatoração para Análise Preditiva

Atualmente, o projeto menciona "Análise Preditiva", "Grafos de Segurança" e "Combinações Tóxicas" em vários lugares (README, `simulate_drift.py`, e relatórios HTML), mas a implementação real dessa lógica é escassa ou simulada:

1.  **Simulação no Firefly Provider**: O `core/governance/providers/firefly_provider.py` atualmente contém uma lógica `mockada` usando apenas a presença de strings de nomes de recursos do terraform no plano JSON (como se houvesse um balde S3 sem criptografia) para gerar recusas, sem usar contexto topológico (relacionamentos).
2.  **Grafo Passivo**: O `schema/security_graph.json` define a estrutura para Combinações Tóxicas e Arestas, mas não existe um componente na Engine de Governança atual que leia esse schema e analise o `plan_json` em relação a ele de maneira estruturada e real para vetar planos dinamicamente.
3.  **Auditor e Sentinel Desconectados**: Os agentes IA, apesar de possuirem descrições ricas, não possuem ferramentas (`tools`) para explorar o grafo diretamente e tomar decisões sobre análise de risco baseada em conexões multi-hop.

## Sugestões de Melhorias

### 1. Criar um `GraphProvider` (Motor de Combinações Tóxicas)
Criar um novo Provider em `core/governance/providers/graph_provider.py` capaz de:
- Parsear o `plan_json` e as modificações propostas.
- Combinar isso com o Gêmeo Digital carregando o estado atual em `schema/security_graph.json`.
- Detectar dinamicamente conexões como "Recurso com acesso à Internet" -> "Acesso via Role IAM" -> "Recurso Sensível (S3/RDS)", implementando um parser simples de topologia.

### 2. Refatorar o `GovernanceManager` e YAML
Atualizar o `GovernanceManager` em `core/governance/manager.py` para carregar nativamente e orquestrar o `GraphProvider`, registrando-o no dicionário e adicionando ao `config/governance_config.yaml`.

### 3. Melhorar as Tools dos Agentes
Fazer com que o `GovernanceManagerTool` (usado pelo Auditor Agent) consiga passar de fato os metadados do grafo ou que existam relatórios claros da infraestrutura para que o Arquiteto e Auditor possam gerar Remediações HCL baseadas na topologia (ex: Remover uma edge tóxica, como o anexo de um Security Group público a uma instância privada).

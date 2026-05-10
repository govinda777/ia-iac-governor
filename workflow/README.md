# 🛠️ Workflow e Ferramentas (Tools)

Este diretório contém as ferramentas customizadas que os agentes do CrewAI utilizam para interagir com o motor de governança e com o inventário de rede.

## 🧰 Ferramentas Principais

- **`GovernanceManagerTool`**: A ferramenta mais importante. Ela serve como a ponte entre o Agente Auditor e o motor de governança (`core/governance`). Ela recebe o código HCL, gera um "mock plan" e executa todas as camadas de validação.
- **`NetworkInventoryTool`**: Utilizada pelo Agente Architect para consultar o IPAM (simulado no `security_graph.json`) e obter CIDRs disponíveis para novas subnets.

## 🔄 Fluxo de Execução da `GovernanceManagerTool`

A `GovernanceManagerTool` encapsula a complexidade de instanciar o motor de governança e processar os resultados para os agentes.

```mermaid
graph TD
    HCL[HCL Code] --> Tool[GovernanceManagerTool]
    Tool --> Parser[HCL Parser / Mock Plan]
    Parser --> Manager[GovernanceManager]

    subgraph "Core Execution"
    Manager --> P1[Cost Layer]
    Manager --> P2[OPA Layer]
    Manager --> P3[Firefly AI Layer]
    end

    P1 --> Collector[Result Collector]
    P2 --> Collector
    P3 --> Collector

    Collector --> Format[Formatter: Approved/Denied]
    Format --> Agent[Auditor Agent]
```

## 📄 Arquivos

- `tools.py`: Implementação das classes que herdam de `BaseTool` do CrewAI. Define o nome, descrição e a lógica de execução (`_run`) de cada ferramenta.

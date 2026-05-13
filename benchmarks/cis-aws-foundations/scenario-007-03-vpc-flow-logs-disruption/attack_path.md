# Caminho do Ataque: 03 Vpc Flow Logs Disruption

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[Role Atacante]:::attacker -->|iam:DeleteRolePolicy| B(Role do Flow Logs):::target
    B --> C{Desativação de Monitoramento de Rede}:::impact
```

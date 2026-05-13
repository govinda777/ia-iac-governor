# Caminho do Ataque: 01 Cross Account Passrole Escalation

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[Usuário Dev (Sandbox)]:::attacker -->|sts:AssumeRole (Cross-Account)| B(Role Administrativa (Prod)):::target
    B --> C{Takeover Total da Conta Prod}:::impact
```

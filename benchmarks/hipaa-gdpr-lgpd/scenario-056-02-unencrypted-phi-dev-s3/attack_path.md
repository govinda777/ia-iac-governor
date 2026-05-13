# Caminho do Ataque: 02 Unencrypted Phi Dev S3

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[DB Criptografado (Prod)]:::attacker -->|Cria Réplica sem Criptografia| B(DB Instance Pública (Sandbox)):::target
    B --> C{Vazamento de Dados SP 800-53}:::impact
```

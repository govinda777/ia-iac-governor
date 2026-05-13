# Caminho do Ataque: 05 Dormant Unrotated Kms Keys

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[EC2 Comprometida (Dev)]:::attacker -->|kms:PutKeyPolicy| B(KMS Key do CloudTrail (Sec)):::target
    B --> C{Cegueira de Auditoria Global}:::impact
```

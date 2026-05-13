# Caminho do Ataque: 01 Sns Topic Hijacking Phi Leak

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[Tópico SNS PII/PHI (Prod)]:::attacker -->|sns:Subscribe| B(Fila SQS do Atacante (Dev)):::target
    B --> C{Exfiltração Silenciosa de Dados Sensíveis}:::impact
```

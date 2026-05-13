# Caminho do Ataque: 05 Cloudfront Pii Caching

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[Bucket/DB com PHI]:::attacker -->|Configuração Pública Acidental| B(Internet (0.0.0.0/0)):::target
    B --> C{Vazamento Massivo de Dados de Pacientes}:::impact
```

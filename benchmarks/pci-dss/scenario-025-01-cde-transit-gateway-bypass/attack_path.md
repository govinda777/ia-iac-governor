# Caminho do Ataque: 01 Cde Transit Gateway Bypass

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[VPC Dev (Sandbox)]:::attacker -->|Tráfego via TGW| B(Cardholder Data Environment (CDE)):::target
    B --> C{Violação PCI-DSS (Acesso ao CDE)}:::impact
```

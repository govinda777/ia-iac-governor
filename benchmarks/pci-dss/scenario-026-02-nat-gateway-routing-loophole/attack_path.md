# Caminho do Ataque: 02 Nat Gateway Routing Loophole

Este diagrama ilustra a topologia da vulnerabilidade e o caminho causal que o Agente IA-IaC Governor detecta.

```mermaid
graph TD
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef target fill:#c4e1f9,stroke:#333,stroke-width:2px;
    classDef impact fill:#f9f5c4,stroke:#333,stroke-width:2px;

    A[DB do CDE (Prod)]:::attacker -->|Tráfego Egress via NAT| B(IP do Atacante (Internet)):::target
    B --> C{Exfiltração de Cartões (PAN)}:::impact
```

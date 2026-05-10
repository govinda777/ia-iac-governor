# 🤖 Agentes de Governança

Esta pasta contém as definições dos agentes e tarefas baseados no framework **CrewAI**, responsáveis pela orquestração inteligente da governança de infraestrutura.

## 👥 Agentes Principais

- **Architect (Arquiteto):** Responsável por gerar código HCL seguro e em conformidade, utilizando Golden Paths e Custom Providers.
- **Auditor (Auditor):** Realiza a auditoria técnica do código gerado, utilizando o `GovernanceManagerTool` para validar camadas de custo, conformidade e segurança.
- **Sentinel (Sentinela):** Monitora o ambiente em busca de drifts (desvios) e combinações tóxicas de recursos.

## 🔄 Fluxo de Trabalho

O diagrama abaixo ilustra como os agentes interagem durante o ciclo de vida de uma solicitação de infraestrutura.

```mermaid
sequenceDiagram
    participant U as Usuário/Intent
    participant Ar as Agente Architect
    participant Au as Agente Auditor
    participant GM as Governance Manager Tool
    participant S as Agente Sentinel

    U->>Ar: Solicitação de Infraestrutura
    Ar->>Ar: Gera HCL (Golden Paths / Provedor Governor)
    Ar->>Au: Envia HCL para Auditoria
    Au->>GM: Valida HCL (Custo, OPA, IA)
    GM-->>Au: Resultado (Approved/Denied + Remediation)

    alt Denied
        Au->>Ar: Feedback Didático & Remediation Patch
        Ar->>Ar: Corrige HCL
        Ar->>Au: Reenvia para Auditoria
    else Approved
        Au->>U: Deploy Autorizado
    end

    loop Monitoramento
        S->>S: Verifica Drift / Security Graph
        alt Drift Detectado
            S->>Ar: Alerta de Drift
            Ar->>Ar: Gera HCL de Correção
        end
    end
```

## 📄 Arquivos

- `agents.py`: Definição das classes, papéis (roles), objetivos (goals) e ferramentas (tools) de cada agente.
- `tasks.py`: Definição das tarefas específicas executadas pelos agentes, incluindo descrição e saída esperada.

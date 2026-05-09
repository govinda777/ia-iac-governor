# PoC: Governança de Infraestrutura AI-Native com CrewAI e OPA

Esta Prova de Conceito (PoC) demonstra como a Inteligência Artificial (IA) pode ser utilizada para automatizar a governança de infraestrutura, indo além de simples bloqueios estáticos para uma abordagem contextual, preditiva e de auto-correção.

## 🚀 Visão Geral

A solução utiliza um framework de **Multi-Agentes (CrewAI)** para simular o ciclo de vida de criação e auditoria de infraestrutura (IaC). O diferencial desta PoC é a integração entre políticas rígidas (**Open Policy Agent - OPA**), estimativa de custos e análise de contexto (**Security Graph**).

### Componentes Principais:
1.  **Agente Arquiteto:** Gera código Terraform baseado na intenção do usuário e ferramentas de IPAM. Realiza a auto-remediação.
2.  **Agente Auditor:** Valida o código contra políticas Rego (Segurança e FinOps) e interpreta erros.
3.  **Agente Sentinel:** Analisa o ambiente em busca de "Combinações Tóxicas" e detecta Drifts (ClickOps).
4.  **OPA (Open Policy Agent):** A âncora da verdade para conformidade técnica e financeira.

---

## 🛠️ Casos de Uso Implementados

| Categoria | Caso de Uso | Problema Resolvido | Estratégia |
| :--- | :--- | :--- | :--- |
| **PCI-DSS** | Criptografia Mandatória | Vazamento de dados em repouso | OPA + Plan JSON |
| **Networking** | IPAM Automático | Conflito de rede e sobreposição | NetworkInventoryTool |
| **IAM** | Permissions Boundaries | Privilégios excessivos (Admin) | Injeção Automática + OPA |
| **FinOps** | Limite de Gasto ($100) | Orçamento estourado sem aviso | CloudCostEstimatorTool + OPA |
| **Dia 2** | Detecção de ClickOps | Alterações manuais inseguras | Drift Detection & Auto-Remediation |

---

## 📂 Estrutura do Repositório

- `agents/`: Definições de agentes e tarefas.
- `policies/`: Políticas Rego (PCI, FinOps, IAM).
- `workflow/`: Ferramentas customizadas (Cost, IPAM, OPA).
- `golden_paths/`: Módulos Terraform endurecidos.
- `examples/`: Cenários de violação e conformidade para teste.
- `schema/`: Contexto do ambiente (`security_graph.json`).
- `simulate_poc.py`: Script de demonstração do ciclo de criação.
- `simulate_drift.py`: Script de demonstração de remediação de drift.

---

## 🚦 Como Executar

### 1. Pré-requisitos
- Python 3.10+
- OPA (Open Policy Agent) instalado localmente.

### 2. Instalação
```bash
pip install -r requirements.txt
# Se necessário:
pip install crewai crewai_tools
```

### 3. Execução (Demonstrações)
Para ver o ciclo de **Criação e Auto-Correção**:
```bash
python3 simulate_poc.py
```

Para ver o ciclo de **Detecção e Remediação de Drift**:
```bash
python3 simulate_drift.py
```

---

## 👨‍💻 Jornadas Demonstradas

### Jornada 1: O Ciclo de Auto-Correção
O desenvolvedor solicita um recurso (ex: RDS). O Arquiteto gera o código, mas o Auditor detecta que falta criptografia e que o custo excede o limite. O Arquiteto recebe o feedback, ajusta o recurso e reaplica, garantindo o deploy seguro sem intervenção humana.

### Jornada 2: A Sentinela do Dia 2
Uma porta SSH é aberta manualmente no console da AWS (ClickOps). O Sentinel detecta a diferença em relação ao Git, o Auditor avalia o risco como crítico e o Arquiteto gera automaticamente o HCL de correção para restaurar o estado desejado.

---

*Criado para fins de demonstração de Governança Moderna e Engenharia de Plataforma.*

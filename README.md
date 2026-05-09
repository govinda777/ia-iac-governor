# PoC: Governança de Infraestrutura AI-Native com CrewAI e OPA

Esta Prova de Conceito (PoC) demonstra como a Inteligência Artificial (IA) pode ser utilizada para automatizar a governança de infraestrutura, indo além de simples bloqueios estáticos para uma abordagem contextual, preditiva e de auto-correção.

## 🚀 Visão Geral

A solução utiliza um framework de **Multi-Agentes (CrewAI)** para simular o ciclo de vida de criação e auditoria de infraestrutura (IaC). O diferencial desta PoC é a integração entre políticas rígidas (**Open Policy Agent - OPA**) e análise de contexto (**Security Graph**).

### Componentes Principais:
1.  **Agente Arquiteto:** Gera código Terraform baseado na intenção do usuário.
2.  **Agente Auditor:** Valida o código contra políticas OOTB (Rego) e interpreta erros.
3.  **Agente Sentinel:** Analisa o ambiente (Grafo de Segurança) em busca de "Combinações Tóxicas".
4.  **OPA (Open Policy Agent):** Atua como a "âncora da verdade" para conformidade técnica.

---

## 🛠️ Especificações

### Funcionais
- **RF01:** Conversão de linguagem natural em código Terraform (HCL).
- **RF02:** Injeção automática de guardrails (Criptografia, Tags, Public Access Block).
- **RF03:** Ciclo de reflexão: a IA corrige o próprio código se for negado pelo Auditor.
- **RF04:** Detecção de riscos contextuais via Grafo de Segurança.

### Não Funcionais
- **RNF01:** Segurança: A IA sugere, mas o OPA garante o bloqueio final.
- **RNF02:** Auditabilidade: Logs detalhados do "raciocínio" dos agentes.
- **RNF03:** Extensibilidade: Fácil adição de novas regras Rego no diretório `policies/`.

---

## 📂 Estrutura do Repositório

- `agents/`: Definições de agentes e tarefas (Python/CrewAI).
- `policies/`: Políticas OOTB escritas em linguagem Rego.
- `schema/`: Contexto do ambiente (ex: `security_graph.json`).
- `main.py`: Orquestrador principal da PoC.
- `simulate_poc.py`: Script de demonstração rápida (Mock Mode).
- `requirements.txt`: Dependências do projeto.

---

## 🚦 Como Executar

### 1. Pré-requisitos
- Python 3.10+
- (Opcional) Chave de API da OpenAI/Anthropic para execução real do CrewAI.

### 2. Instalação
```bash
pip install -r requirements.txt
```

### 3. Execução (Modo Demonstração)
Para ver o fluxo de "raciocínio" dos agentes sem necessidade de uma chave de API:
```bash
python3 simulate_poc.py
```

### 4. Execução Real (Com CrewAI)
Edite o arquivo `main.py` para configurar sua chave de API e altere `use_mock=False`:
```bash
export OPENAI_API_KEY='sua_chave_aqui'
python3 main.py
```

---

## 👨‍💻 Jornadas do Usuário

### Jornada 1: O Desenvolvedor Ágil
O desenvolvedor solicita um recurso simples: *"Preciso de um bucket S3 para logs"*. A IA gera o código já com as tags da empresa e criptografia habilitada, economizando tempo de consulta à documentação.

### Jornada 2: O Auditor de Segurança
O código gerado passa por um "juiz" (OPA). Se houver uma falha (ex: porta 22 aberta), a IA não apenas bloqueia, mas **explica o porquê** e **sugere a correção exata**, educando o desenvolvedor no processo.

### Jornada 3: O Sentinel (Contexto)
A IA percebe que, embora o bucket seja privado, a Role associada à instância que o acessará tem permissões excessivas e a instância está em uma rede pública. A IA sugere o **Princípio do Menor Privilégio** automaticamente.

---

## 📊 Tabela de Comparação

| Característica | Modelo Tradicional | Modelo AI-Native (PoC) |
| :--- | :--- | :--- |
| **Implementação** | Revisão Manual / Tickets | Agentes de IA Autônomos |
| **Conformidade** | Reativa (pós-deploy) | Preventiva (na geração) |
| **Correção** | Manual pelo Dev | Auto-remediação sugerida |
| **Contexto** | Ignorado por regras fixas | Analisado via Grafos |

---

*Criado para fins de demonstração de Governança Moderna e Engenharia de Plataforma.*

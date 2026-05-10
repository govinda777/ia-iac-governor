# 🧠 Core Engine

O diretório `core/` contém a lógica central e os motores de processamento da plataforma IA-IaC Governor.

## 🏗️ Estrutura

- **`governance/`**: O motor de governança modular e plugável. Aqui reside a inteligência que orquestra as validações de conformidade, custo e segurança.

## 🚀 Papel do Core

O Core atua como o "cérebro" do sistema, transformando planos de infraestrutura brutos em decisões de conformidade estruturadas. Ele é projetado para ser:

1.  **Agnóstico:** Capaz de processar diferentes tipos de regras.
2.  **Extensível:** Permite a adição de novos provedores de governança sem alterar a lógica principal.
3.  **Contextual:** Mantém um estado compartilhado durante a validação para que um provedor possa usar informações de outro.

Para detalhes sobre a implementação do motor de governança, consulte o [README em core/governance](./governance/README.md).

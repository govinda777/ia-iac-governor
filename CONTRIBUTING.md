# Guia de Contribuição - IA-IaC Governor

Obrigado por seu interesse em contribuir para o **IA-IaC Governor**! Como um produto de engenharia de plataforma, valorizamos contribuições que tornem a infraestrutura mais segura, padronizada e fácil de usar.

## 🌟 O Conceito de "Caminhos Dourados" (Golden Paths)

Nossa filosofia de contribuição baseia-se em criar **Golden Paths**. Um Caminho Dourado é uma abstração de infraestrutura (módulo) que já nasce em conformidade com as melhores práticas de segurança e governança da organização.

Ao contribuir com um novo módulo para o nosso **Private Module Registry**, você está ajudando outros times a "caírem no poço do sucesso", onde o caminho mais fácil é também o caminho mais seguro.

---

## 🚀 Tutorial do Dia 1: Sua Primeira Contribuição

Se você é novo no projeto, siga estes passos para começar:

### 1. Configure seu Ambiente
Certifique-se de ter o Python 3.10+ e o OPA instalados. Clone o repositório e instale as dependências:
```bash
git clone https://github.com/seu-usuario/ia-iac-governor.git
cd ia-iac-governor
pip install -r requirements.txt
```

### 2. Explore os Golden Paths Existentes
Veja os módulos em `golden_paths/`. Eles servem como referência para o padrão de código HCL esperado.

### 3. Crie uma Nova Política (OPA/Rego)
Se você quer adicionar um novo guardrail:
1. Vá para a pasta `policies/`.
2. Crie um novo arquivo `.rego`.
3. Escreva sua política focando no recurso que deseja validar.
4. Teste sua política localmente usando `opa test`.

### 4. Adicione um Novo Caso de Teste
Adicione um exemplo de HCL em `examples/` que viole sua nova política e outro que esteja em conformidade. Rode o script `python3 test_examples.py` para validar.

---

## 🛠️ Como Contribuir

### Novos Módulos (Golden Paths)
- Os módulos devem ser genéricos o suficiente para serem reutilizados.
- Devem incluir documentação clara das variáveis de entrada e saída.
- Devem, preferencialmente, utilizar o Custom Provider `governor` para recursos sensíveis.

### Políticas de Governança
- Políticas devem ser classificadas por severidade: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- Use nomes descritivos para as regras Rego para facilitar o feedback didático da IA.

### Melhorias no Core
- Se você deseja melhorar os agentes de IA ou o `GovernanceManager`, abra uma Issue para discutirmos a abordagem antes de iniciar o desenvolvimento.

## 📝 Processo de Submissão

1. Crie uma branch para sua alteração: `git checkout -b feat/meu-novo-golden-path`.
2. Faça o commit das suas alterações com mensagens claras.
3. Garanta que todos os testes passem: `python3 test_examples.py` e `python3 simulate_poc.py`.
4. Abra um Pull Request detalhando o que foi alterado e qual problema de governança está sendo resolvido.

---

*Juntos, estamos construindo o futuro da governança de infraestrutura autônoma!*

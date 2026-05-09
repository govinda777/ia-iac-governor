O arquivo `security_graph.json` no repositório indicado define o **esquema de dados** para um **Cloud Security Graph** (Grafo de Segurança na Nuvem). Este modelo é a base tecnológica para uma governança moderna e preditiva, permitindo que a plataforma visualize a infraestrutura não como uma lista estática, mas como uma rede de entidades interconectadas.

Abaixo, explico os componentes desse esquema e como eles resolvem problemas complexos de segurança e auditoria:

### 1. A Estrutura do Grafo: Nós e Arestas

O esquema mapeia a infraestrutura seguindo o paradigma de grafos, o que permite uma visão idêntica à de um invasor:

* 
**Nós (Nodes - O "Quê"):** Representam os ativos discretos da nuvem, como instâncias EC2, buckets S3, usuários IAM, roles e grupos de segurança. Cada nó possui metadados que definem sua criticidade e estado de conformidade.


* 
**Arestas (Edges - O "Como"):** Definem as relações e permissões entre os nós. Uma aresta pode representar um tráfego de rede permitido, uma política de confiança IAM (`sts:AssumeRole`) ou uma relação de contenção (ex: uma VM que "está dentro" de uma Subnet específica).



### 2. Identificação de "Combinações Tóxicas"

A principal vantagem deste esquema JSON é permitir que a plataforma identifique riscos sistêmicos que ferramentas de lista simples ignoram:

* 
**Exemplo:** O grafo pode detectar que uma instância EC2 exposta à internet possui uma Role anexada que, por sua vez, tem permissão para ler um bucket S3 com dados sensíveis (PCI).


* 
**Caminho de Ataque (Attack Path):** O esquema permite consultas que atravessam múltiplos "pulos" (multi-hop) para revelar como um erro simples de configuração em um ponto pode comprometer um ativo crítico (as "joias da coroa") em outro ponto.



### 3. Implementação e Consultas (Cypher/Rego)

O esquema é projetado para ser consumido por motores de busca e políticas:

* 
**Consultas de Padrão:** Utilizando linguagens como **Cypher**, a plataforma pode buscar padrões como: *"Encontre todos os bancos de dados acessíveis por instâncias que possuem chaves de acesso expostas"*.


* 
**Validação via OPA:** Regras escritas em **Rego** podem analisar o grafo gerado a partir do plano do Terraform (`terraform plan JSON`) para bloquear o deploy caso o novo recurso crie um caminho de ataque lateral perigoso.



### 4. Integração com IA (Supercharger Analítico)

Ao definir esse esquema, a plataforma permite que a **IA atue de forma preditiva**:

* 
**Análise "What-if":** A IA pode simular uma alteração proposta no código e prever, através do grafo, se aquela mudança criará uma nova vulnerabilidade antes mesmo da infraestrutura ser criada.


* 
**Linguagem Natural:** Com o esquema bem definido, a IA pode traduzir perguntas simples como *"Quais recursos PCI estão expostos?"* em travessias complexas no grafo de segurança.



### Resumo da Importância para a PoC

Este arquivo JSON não é apenas uma documentação; é o **"Gêmeo Digital"** (Digital Twin) da realidade de segurança da sua nuvem. Ele permite que sua governança saia do modelo reativo (limpar alertas) e passe para a redução estratégica de riscos, focando nos caminhos de ataque que realmente importam para a organização.

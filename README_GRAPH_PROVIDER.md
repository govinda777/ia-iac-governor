# GraphProvider: Análise Preditiva e Combinações Tóxicas

O `GraphProvider` implementa um mecanismo avançado de Análise Preditiva dentro do IA-IaC Governor.
Ao invés de verificar regras fixas linha a linha (como portas abertas em um Security Group), o `GraphProvider` avalia o plano do Terraform utilizando uma perspectiva orientada a Grafos, permitindo detectar **"Combinações Tóxicas"** na topologia da infraestrutura proposta.

## Como os Riscos são Calculados?

Diferente de políticas estáticas do OPA, os riscos no `GraphProvider` vêm diretamente do **Gêmeo Digital** (Digital Twin) de Segurança da empresa.
O arquivo base é o `schema/security_graph.json`. Ele define a topologia atual e modela os vetores de ataque conhecidos pela empresa.

O motor do provedor é projetado sem uso de bibliotecas pesadas externas (como o `networkx`) para garantir sua execução transparente em ambientes fechados (Air Gapped CI).

### O Papel do `schema/security_graph.json`
Este schema age como uma base de conhecimento. A propriedade `risks` dentro deste JSON contém as definições de todas as combinações perigosas para o negócio atual.

```json
  "risks": [
    {
      "id": "risk-01",
      "name": "Toxic Combination: Public Exposure + S3 Full Access",
      "severity": "CRITICAL",
      "description": "The instance 'instance-app-01' is in a public subnet and has full access to S3. If compromised, an attacker can exfiltrate all data from S3 buckets."
    }
  ]
```

### O Ciclo de Vida da Validação Preditiva

1. **Extração de Riscos (`graph_data.get("risks", [])`)**:
   Durante a execução, o `GraphProvider` carrega o schema e extrai dinamicamente a matriz de `risks` conhecidos listados no Gêmeo Digital.
2. **Parsing do Terraform Plan**: O provedor disseca a saída do `terraform plan` convertida em JSON (`resource_changes`), simulando as ligações propostas na infraestrutura antes do apply.
3. **Avaliação Semântica (Heurísticas Baseadas no Grafo)**:
   - Para o `risk-01`, o provedor vasculha o plano atrás de três elementos chaves conectando-os: Instâncias EC2 (`aws_instance`), Buckets S3 (`aws_s3_bucket`) e Exposição Pública (`map_public_ip_on_launch` configurado para `true` em uma subnet, ou permissões `"0.0.0.0/0"`).
   - Se os atributos do Terraform batem com os padrões listados nos nós e arestas de um "Attack Path" catalogado, a combinação tóxica é materializada e a pipeline é **interrompida**.
   - As heurísticas são programadas de maneira agnóstica para identificar os riscos não via strings brutas, mas iterando através das instâncias JSON `resource_changes` avaliando as mudanças na árvore de dependência.

## O Papel do Fallback (Mock Parsing) em CI
Muitas vezes em esteiras CI de segurança, comandos como `terraform init` ou `terraform plan` falham devido a bloqueios na rede, ausência de credenciais, ou `Inconsistent dependency lock file` ao lidar com providers customizados locais (ex: Provider *Governor* na `registry.terraform.io`).

Para não travar a governança estática de atuar quando o plano falha, o `GraphProvider` se beneficia de um parsing via Expressões Regulares em cima do arquivo raw (`plan_json["raw_hcl"]`) implementado como "Fallback" seguro no `GovernanceManagerTool`.
Isso nos permite simular propriedades fundamentais iterando nativamente sem a máquina de estados completa do terraform, mantendo a detecção de riscos funcional em qualquer ambiente de pipeline.

## Lições Aprendidas
Durante a implementação da Análise Preditiva e do `GraphProvider`, obtivemos as seguintes conclusões:
- **Resiliência de Pipeline é Fundamental:** Utilizar a versão nativa do comando `terraform plan` é preferível, mas falhas são frequentes em CIs corporativos sem acesso direto a todos os providers locais. O mecanismo de Fallback (que aplica Expressões Regulares de forma robusta e constrói a estrutura básica) garantiu a continuidade sem perder precisão estática, algo crítico em esteiras rígidas de CI/CD.
- **Isolamento Constante (Mock sem Mutação Global):** O uso de fixtures baseados em descritores de arquivos (`tempfile`) evitou a mutabilidade perigosa no pacote `json` global do sistema. Ao arquitetar simuladores de grafos e schemas de testes unitários em ferramentas complexas, o escopo da ação afeta os falsos positivos de validações paralelas.
- **Topologia Estruturada vs Regras Rígidas Estáticas:** Limitar-se à correspondências simples de string provou-se inadequado devido à inabilidade de detectar se um IP exposto interagia com ativos S3 no mesmo escopo ou bloco. O uso da estrutura hierárquica `resource_changes` foi o único caminho para um início consistente na detecção da "Combinação Tóxica".

## Próximos Passos
O aprimoramento da avaliação preditiva deve envolver a expansão dos recursos de mapeamento do grafo e das capacidades nativas, com o objetivo de reduzir o delta para o provisionamento do mundo real:
1. **Modelagem Interativa Completa do Schema:**
   - Ampliar a extração lógica além das heurísticas programáticas (`has_s3` and `has_ec2` and `has_public_exposure`). O ideal será interpretar iterativamente o `"logic": "Node(Account1:Subnet:Public) -> Edge(VPC_Peering) -> Node(Account2:RDS:Production)"` listado nos metadados dos Benchmarks e convertê-los de forma agnóstica para queries em Python.
2. **Avaliação Fidedigna do `raw_hcl` no Fallback:**
   - Incrementar as Regex do Fallback CI do `GovernanceManagerTool` para extrair não apenas que os recursos existem (tipo e nome), mas recuperar atributos simples (`cidr_block`, `public_ip_on_launch`), permitindo que a simulação CI e o HCL Plan possuam os mesmos nós e metadados contextuais, aproximando a eficácia ao JSON do Tofu/Terraform completo.

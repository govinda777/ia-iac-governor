# Documentação Técnica: Integridade do Estado (tfstate) e APIs de Governança

Este documento explica como o recurso `governor_managed_subnet` garante a integridade do estado do Terraform, mesmo quando a API interna de governança sofre alterações.

## Arquitetura "Black Box" e Campos Computed

O segredo para evitar drift indesejado e falhas no `terraform apply` reside no uso estratégico de campos `Computed: true`.

### 1. Desacoplamento da Intenção vs. Implementação
No HCL, o desenvolvedor declara apenas:
```hcl
resource "governor_managed_subnet" "app" {
  project_name = "my-project"
  tier         = "private"
}
```

Campos como `cidr_block`, `vpc_id` e `tags` **não são declarados no HCL**. Eles são marcados como `Computed` no schema do Provider.

### 2. O Ciclo de Vida e Mudanças na API
Se a API de governança mudar o padrão de uma tag (ex: de `Project` para `ProjectID`), o ciclo de vida ocorre da seguinte forma:

1.  **Read Context**: O método `Read` do Provedor busca o estado atual na AWS (via SDK). Ele popula o estado local com o que **realmente existe** na nuvem.
2.  **Plan Context**: O Terraform compara o HCL com o estado. Como `tags` ou `cidr_block` não estão no HCL, o Terraform "confia" no que o Provedor decidir.
3.  **Update Context**: Se a API interna retornar tags diferentes durante um novo `apply`, o Provedor detectará a diferença entre o que está na AWS e o que a API de Governança agora exige. Ele executará a atualização via `ec2.CreateTags`, mantendo o `tfstate` sincronizado com a nova regra de negócio sem exigir que o desenvolvedor altere seu código HCL.

### 3. Idempotência e Drift
*   **Drift de Recriação**: Campos fundamentais como `project_name` e `tier` utilizam `RequiresReplace()`. Se alterados, o Terraform força a destruição e recriação do recurso, garantindo que a governança realoque um novo CIDR se necessário.
*   **Limpeza de Estado**: Se o recurso for deletado manualmente na AWS, o método `Read` detectará o erro `NotFound` e executará `resp.State.RemoveResource(ctx)`. Isso informa ao Terraform que o recurso não existe mais, permitindo que ele seja recriado no próximo `apply`.

## Benefícios para Engenharia de Plataforma
- **Zero Código Legado**: Regras de nomenclatura e alocação de rede ficam na API de governança, não espalhadas em milhares de repositórios Git de aplicações.
- **Soberania**: A plataforma mantém o controle total sobre quais VPCs e faixas de IP são utilizadas, baseando-se apenas no contexto do projeto.

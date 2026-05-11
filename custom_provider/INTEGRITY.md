# Documentação Técnica: Modelo de Orquestração Cross-Departamento

Este documento detalha o funcionamento do Provedor Terraform em um cenário de **Soberania de Infraestrutura**, onde diferentes departamentos são responsáveis pelo provisionamento real.

## Arquitetura de Camadas

Para evitar o acúmulo de "código legado" e misturar responsabilidades, o provedor é dividido em três camadas claras:

1.  **Schema & State (Provedor)**: O arquivo `resource_managed_subnet.go` define **o que** o desenvolvedor quer (intenção) e **como** o Terraform salva isso (estado). Ele não sabe como criar uma VPC ou Subnet.
2.  **Orchestration (API Interna)**: O pacote `governance` (ex: `api.go`) atua como o representante do departamento técnico (Redes, Segurança, etc). Ele recebe a intenção e executa a lógica complexa (ex: criar VPC, verificar CIDRs, aplicar tags globais).
3.  **Cloud Native (SDK)**: O SDK da AWS é utilizado como a ferramenta final de execução, mas sua invocação é encapsulada pela camada de Orquestração.

## Fluxo de Provisionamento "Black Box"

Quando um desenvolvedor executa `terraform apply`:

1.  O Provedor captura o `project_name` e `tier`.
2.  O Provedor chama `governance.ProvisionSubnet()`.
3.  O departamento de Redes (representado pela API) decide a arquitetura:
    *   Verifica se a VPC do projeto já existe. Se não, cria.
    *   Aloca o CIDR correto baseado em regras corporativas.
    *   Cria a Subnet com as tags de conformidade.
4.  A API retorna os IDs (`subnet-xxx`, `vpc-yyy`) para o Provedor.
5.  O Provedor salva esses IDs no `tfstate`.

## Vantagens
*   **Idempotência**: A API de orquestração lida com conflitos e garante que, se o recurso já existir (mesmo que criado por outro processo), o Terraform consiga mapeá-lo.
*   **Segurança**: O desenvolvedor não tem permissão para escolher o CIDR ou a VPC, eliminando o erro humano e garantindo conformidade por design.
*   **Manutenibilidade**: Se o departamento de Redes mudar o fornecedor de nuvem ou o padrão de VPCs, a alteração é feita apenas na camada de Orquestração, sem quebrar o código HCL de milhares de aplicações.

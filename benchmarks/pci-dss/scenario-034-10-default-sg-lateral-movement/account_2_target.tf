# Conta 2 (Alvo / Produção / CDE)
# Certificação: pci-dss
# Cenário: 10 Default Sg Lateral Movement

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Banco de Dados Interno
# Escreva o HCL de produção aqui.

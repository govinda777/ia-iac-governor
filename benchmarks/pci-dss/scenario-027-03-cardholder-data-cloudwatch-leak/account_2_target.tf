# Conta 2 (Alvo / Produção / CDE)
# Certificação: pci-dss
# Cenário: 03 Cardholder Data Cloudwatch Leak

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Recurso de Produção
# Escreva o HCL de produção aqui.

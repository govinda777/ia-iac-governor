# Conta 2 (Alvo / Produção / CDE)
# Certificação: pci-dss
# Cenário: 01 Cde Transit Gateway Bypass

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Cardholder Data Environment (CDE)
# Escreva o HCL de produção aqui.

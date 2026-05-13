# Conta 2 (Alvo / Produção / CDE)
# Certificação: nist-sp-800-53
# Cenário: 03 Boundary Protection Bypass

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: VPC Restrita
# Escreva o HCL de produção aqui.

# Conta 2 (Alvo / Produção / CDE)
# Certificação: nist-sp-800-53
# Cenário: 02 Api Gateway Vpc Link Exfiltration

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: NLB Interno
# Escreva o HCL de produção aqui.

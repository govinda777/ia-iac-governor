# Conta 2 (Alvo / Produção / CDE)
# Certificação: soc2-type2
# Cenário: 09 Route53 Prod To Dev Hijacking

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Recurso de Produção
# Escreva o HCL de produção aqui.

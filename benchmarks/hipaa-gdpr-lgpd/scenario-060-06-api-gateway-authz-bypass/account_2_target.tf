# Conta 2 (Alvo / Produção / CDE)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 06 Api Gateway Authz Bypass

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: NLB Interno
# Escreva o HCL de produção aqui.

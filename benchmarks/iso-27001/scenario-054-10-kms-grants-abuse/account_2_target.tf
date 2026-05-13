# Conta 2 (Alvo / Produção / CDE)
# Certificação: iso-27001
# Cenário: 10 Kms Grants Abuse

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: KMS Key do CloudTrail (Sec)
# Escreva o HCL de produção aqui.

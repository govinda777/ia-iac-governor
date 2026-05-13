# Conta 2 (Alvo / Produção / CDE)
# Certificação: cis-aws-foundations
# Cenário: 09 Kms Cmk Hijacking

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: KMS Key do CloudTrail (Sec)
# Escreva o HCL de produção aqui.

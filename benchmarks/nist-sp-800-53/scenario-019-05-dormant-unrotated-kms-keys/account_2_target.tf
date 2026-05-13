# Conta 2 (Alvo / Produção / CDE)
# Certificação: nist-sp-800-53
# Cenário: 05 Dormant Unrotated Kms Keys

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: KMS Key do CloudTrail (Sec)
# Escreva o HCL de produção aqui.

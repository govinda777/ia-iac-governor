# Conta 2 (Alvo / Produção / CDE)
# Certificação: cis-aws-foundations
# Cenário: 06 Root Access Eventbridge

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Lambda Admin
# Escreva o HCL de produção aqui.

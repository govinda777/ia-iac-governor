# Conta 2 (Alvo / Produção / CDE)
# Certificação: iso-27001
# Cenário: 05 Sqs Queue Hijacking

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Fila SQS do Atacante (Dev)
# Escreva o HCL de produção aqui.

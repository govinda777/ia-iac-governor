# Conta 1 (Atacante / Sandbox)
# Certificação: cis-aws-foundations
# Cenário: 07 S3 Public Access Override

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Atacante Sandbox
# Escreva o HCL vulnerável aqui.

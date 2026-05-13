# Conta 1 (Atacante / Sandbox)
# Certificação: nist-sp-800-53
# Cenário: 05 Dormant Unrotated Kms Keys

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: EC2 Comprometida (Dev)
# Escreva o HCL vulnerável aqui.

# Conta 1 (Atacante / Sandbox)
# Certificação: iso-27001
# Cenário: 09 Sagemaker Notebook Vpc Leak

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Atacante Sandbox
# Escreva o HCL vulnerável aqui.

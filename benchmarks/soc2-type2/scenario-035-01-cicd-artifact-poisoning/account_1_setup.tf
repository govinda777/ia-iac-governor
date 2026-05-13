# Conta 1 (Atacante / Sandbox)
# Certificação: soc2-type2
# Cenário: 01 Cicd Artifact Poisoning

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Usuário Dev (Sandbox)
# Escreva o HCL vulnerável aqui.

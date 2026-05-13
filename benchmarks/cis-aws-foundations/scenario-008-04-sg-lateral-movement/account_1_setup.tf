# Conta 1 (Atacante / Sandbox)
# Certificação: cis-aws-foundations
# Cenário: 04 Sg Lateral Movement

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Instância Bastion Pública
# Escreva o HCL vulnerável aqui.

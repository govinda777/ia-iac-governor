# Conta 1 (Atacante / Sandbox)
# Certificação: pci-dss
# Cenário: 09 Ssm Run Command Abuse Cde

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Atacante Sandbox
# Escreva o HCL vulnerável aqui.

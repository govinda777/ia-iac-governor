# Conta 2 (Alvo / Produção / CDE)
# Certificação: pci-dss
# Cenário: 05 Direct Connect Lateral Movement

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Recurso de Produção
# Escreva o HCL de produção aqui.

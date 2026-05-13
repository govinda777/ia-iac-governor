# Conta 2 (Alvo / Produção / CDE)
# Certificação: pci-dss
# Cenário: 02 Nat Gateway Routing Loophole

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: IP do Atacante (Internet)
# Escreva o HCL de produção aqui.

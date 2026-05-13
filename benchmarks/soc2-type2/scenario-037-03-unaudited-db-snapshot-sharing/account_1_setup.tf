# Conta 1 (Atacante / Sandbox)
# Certificação: soc2-type2
# Cenário: 03 Unaudited Db Snapshot Sharing

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Admin de DB (Prod)
# Escreva o HCL vulnerável aqui.

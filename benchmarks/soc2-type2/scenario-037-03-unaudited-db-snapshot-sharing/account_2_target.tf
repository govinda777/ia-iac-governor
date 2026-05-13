# Conta 2 (Alvo / Produção / CDE)
# Certificação: soc2-type2
# Cenário: 03 Unaudited Db Snapshot Sharing

provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Conta AWS Externa
# Escreva o HCL de produção aqui.

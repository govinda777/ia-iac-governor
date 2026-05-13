# Conta 1 (Atacante / Sandbox)
# Certificação: soc2-type2
# Cenário: 03 Unaudited Db Snapshot Sharing

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Admin de DB (Prod)
# Escreva o HCL vulnerável aqui.

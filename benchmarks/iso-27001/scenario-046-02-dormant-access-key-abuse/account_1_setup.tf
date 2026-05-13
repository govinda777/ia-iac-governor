# Conta 1 (Atacante / Sandbox)
# Certificação: iso-27001
# Cenário: 02 Dormant Access Key Abuse

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Access Key Abandonada
# Escreva o HCL vulnerável aqui.

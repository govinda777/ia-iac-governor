# Conta 1 (Atacante / Sandbox)
# Certificação: iso-27001
# Cenário: 10 Kms Grants Abuse

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: EC2 Comprometida (Dev)
# Escreva o HCL vulnerável aqui.

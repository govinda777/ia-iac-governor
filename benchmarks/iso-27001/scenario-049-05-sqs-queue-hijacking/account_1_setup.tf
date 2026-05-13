# Conta 1 (Atacante / Sandbox)
# Certificação: iso-27001
# Cenário: 05 Sqs Queue Hijacking

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Tópico SNS PII/PHI (Prod)
# Escreva o HCL vulnerável aqui.

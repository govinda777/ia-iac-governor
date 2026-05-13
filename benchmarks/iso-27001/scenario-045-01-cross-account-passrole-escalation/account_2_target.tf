# Conta 2 (Alvo / Produção / CDE)
# Certificação: iso-27001
# Cenário: 01 Cross Account Passrole Escalation

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Role Administrativa (Prod)
# Escreva o HCL de produção aqui.

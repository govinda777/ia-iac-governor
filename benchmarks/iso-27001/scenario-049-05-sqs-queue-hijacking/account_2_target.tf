# Conta 2 (Alvo / Produção / CDE)
# Certificação: iso-27001
# Cenário: 05 Sqs Queue Hijacking

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Fila SQS do Atacante (Dev)
# Escreva o HCL de produção aqui.

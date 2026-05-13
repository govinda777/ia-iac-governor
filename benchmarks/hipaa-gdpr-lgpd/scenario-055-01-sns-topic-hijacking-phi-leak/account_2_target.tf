# Conta 2 (Alvo / Produção / CDE)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 01 Sns Topic Hijacking Phi Leak

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Fila SQS do Atacante (Dev)
# Escreva o HCL de produção aqui.

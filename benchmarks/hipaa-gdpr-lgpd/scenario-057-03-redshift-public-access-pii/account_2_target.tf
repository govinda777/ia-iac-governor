# Conta 2 (Alvo / Produção / CDE)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 03 Redshift Public Access Pii

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: Internet (0.0.0.0/0)
# Escreva o HCL de produção aqui.

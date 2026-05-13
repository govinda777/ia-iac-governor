# Conta 1 (Atacante / Sandbox)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 03 Redshift Public Access Pii

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Bucket/DB com PHI
# Escreva o HCL vulnerável aqui.

# Conta 1 (Atacante / Sandbox)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 07 Dynamodb Pii Export Insecure S3

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Bucket/DB com PHI
# Escreva o HCL vulnerável aqui.

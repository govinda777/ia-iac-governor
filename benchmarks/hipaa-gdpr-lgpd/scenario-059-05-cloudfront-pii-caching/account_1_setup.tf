# Conta 1 (Atacante / Sandbox)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 05 Cloudfront Pii Caching

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Bucket/DB com PHI
# Escreva o HCL vulnerável aqui.

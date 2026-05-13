# Conta 1 (Atacante / Sandbox)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 01 Sns Topic Hijacking Phi Leak

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Tópico SNS PII/PHI (Prod)
# Escreva o HCL vulnerável aqui.

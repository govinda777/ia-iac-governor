# Conta 1 (Atacante / Sandbox)
# Certificação: hipaa-gdpr-lgpd
# Cenário: 02 Unencrypted Phi Dev S3

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: DB Criptografado (Prod)
# Escreva o HCL vulnerável aqui.

# Conta 2 (Alvo / Produção / CDE)
# Certificação: soc2-type2
# Cenário: 01 Cicd Artifact Poisoning

provider "aws" {
  alias  = "prod"
  region = "us-east-1"
}

# [TODO] O Agente deve proteger este recurso: S3 de Pipeline CI/CD (Prod)
# Escreva o HCL de produção aqui.

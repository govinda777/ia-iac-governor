# Conta 1 (Atacante / Sandbox)
# Certificação: nist-sp-800-53
# Cenário: 03 Boundary Protection Bypass

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: Client VPN Público
# Escreva o HCL vulnerável aqui.

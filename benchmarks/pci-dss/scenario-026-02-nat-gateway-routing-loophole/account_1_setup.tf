# Conta 1 (Atacante / Sandbox)
# Certificação: pci-dss
# Cenário: 02 Nat Gateway Routing Loophole

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# [TODO] O Agente deve analisar este recurso: DB do CDE (Prod)
# Escreva o HCL vulnerável aqui.

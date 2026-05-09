# Exemplo de infraestrutura governada utilizando o Custom Provider e Golden Path

module "minha_app" {
  source = "../golden_paths/standard-application"

  app_name         = "pagamentos-v2"
  environment      = "prod"
  compliance_level = "pci"
}

# Recurso nativo que deve ser BLOQUEADO pelo Auditor (OPA)
resource "aws_vpc" "vulneravel" {
  cidr_block = "10.10.0.0/16"
  tags = {
    Name = "VPC-Nao-Governada"
  }
}

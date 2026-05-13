# Conta 1 (Atacante / Sandbox)
# Certificação: cis-aws-foundations
# Cenário: 01-cloudtrail-evasion-kms

provider "aws" {
  alias  = "sandbox"
  region = "us-east-1"
}

# Uma EC2 em Sandbox (Dev) com uma Role genérica
resource "aws_iam_role" "dev_ec2_role" {
  provider = aws.sandbox
  name     = "DevEC2Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Vulnerabilidade Topológica Crítica:
# Esta policy parece inofensiva ("só pode rodar kms:* na conta de sandbox"),
# MAS se combinada com o erro do outro lado (A policy da chave na conta Sec permite que account_id_sandbox mexa),
# o atacante pode reconfigurar o KMS do CloudTrail!
resource "aws_iam_role_policy" "dev_ec2_policy" {
  provider = aws.sandbox
  name     = "DevEC2Policy_KMS_Excessivo"
  role     = aws_iam_role.dev_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "kms:PutKeyPolicy",
          "kms:DescribeKey"
        ]
        Resource = "*" # Permite atualizar políticas de QUALQUER chave (que ele tenha acesso via Key Policy)
      }
    ]
  })
}

resource "aws_instance" "dev_box" {
  provider = aws.sandbox
  ami           = "ami-1234567890abcdef0"
  instance_type = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.dev_profile.name

  tags = {
    Name = "Compromised Dev EC2"
  }
}

resource "aws_iam_instance_profile" "dev_profile" {
  provider = aws.sandbox
  name     = "DevEC2Profile"
  role     = aws_iam_role.dev_ec2_role.name
}

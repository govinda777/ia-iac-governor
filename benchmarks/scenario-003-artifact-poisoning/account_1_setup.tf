# Account 1 (Dev/Sandbox) - 111111111111

# Qualquer role nesta conta pode ser o vetor de ataque
resource "aws_iam_role" "dev_role" {
  name = "DeveloperRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" } }]
  })
}

# A role não precisa de permissão explícita no IAM se o S3 permitir o OrgID

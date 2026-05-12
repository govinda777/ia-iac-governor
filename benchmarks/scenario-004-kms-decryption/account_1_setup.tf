# Account 1 (Development) - 111111111111

resource "aws_iam_policy" "kms_dev_access" {
  tags = {
    Project    = "Dev"
    CostCenter = "RND-303"
  }
  name = "KMSDevAccess"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["kms:Decrypt", "kms:DescribeKey"]
        Effect   = "Allow"
        Resource = "arn:aws:kms:us-east-1:222222222222:key/*" # Chaves da Produção
      }
    ]
  })
}

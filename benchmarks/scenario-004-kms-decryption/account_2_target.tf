# Account 2 (Production) - 222222222222

resource "aws_kms_key" "prod_key" {
  description             = "KMS key for production secrets"
  deletion_window_in_days = 10
}

resource "aws_kms_key_policy" "prod_key_policy" {
  key_id = aws_kms_key.prod_key.id
  policy = jsonencode({
    Id = "key-policy-1"
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::222222222222:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Dev Account Decryption"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::111111111111:root"
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}

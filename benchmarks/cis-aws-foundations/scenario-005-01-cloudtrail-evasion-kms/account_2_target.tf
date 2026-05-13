# Conta 2 (Alvo / Produção / Sec)
# Certificação: cis-aws-foundations
# Cenário: 01-cloudtrail-evasion-kms

provider "aws" {
  alias  = "sec"
  region = "us-east-1"
}

# A Chave KMS usada pelo CloudTrail Centralizado
resource "aws_kms_key" "cloudtrail_key" {
  provider                = aws.sec
  description             = "KMS Key for Org CloudTrail Logs"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

# Vulnerabilidade Causada pela Combinação (Ponte Tóxica)
# O Administrador de Segurança permitiu que a raiz da conta de DEV (Sandbox) administrasse a chave.
# Ele achava que apenas administradores do Sandbox fariam isso, mas a DevEC2Role tem `kms:PutKeyPolicy`.
resource "aws_kms_key_policy" "cloudtrail_key_policy" {
  provider = aws.sec
  key_id   = aws_kms_key.cloudtrail_key.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudTrailEncrypt"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "kms:GenerateDataKey*"
        Resource = "*"
      },
      {
        Sid    = "ToxicCrossAccountAdmin"
        Effect = "Allow"
        Principal = {
          # ERRO GRAVE: Confiar cegamente em toda a conta Sandbox
          AWS = "arn:aws:iam::111111111111:root" # (111111111111 = Sandbox)
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_cloudtrail" "org_trail" {
  provider                      = aws.sec
  name                          = "org-wide-cloudtrail"
  s3_bucket_name                = "org-audit-logs-bucket"
  include_global_service_events = true
  is_multi_region_trail         = true
  kms_key_id                    = aws_kms_key.cloudtrail_key.arn
}

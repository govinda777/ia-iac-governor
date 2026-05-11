# Account 2 (Production) - 222222222222

resource "aws_s3_bucket" "artifacts" {
  bucket = "prod-ci-cd-artifacts-222222"
}

resource "aws_s3_bucket_policy" "allow_org_write" {
  bucket = aws_s3_bucket.artifacts.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowOrgWriteAccess"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:PutObject", "s3:PutObjectAcl"]
        Resource  = "${aws_s3_bucket.artifacts.arn}/*"
        Condition = {
          StringEquals = {
            "aws:PrincipalOrgID" = "o-123456789"
          }
        }
      }
    ]
  })
}

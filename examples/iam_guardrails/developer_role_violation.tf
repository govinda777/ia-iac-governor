resource "aws_iam_role" "developer" {
  name = "DeveloperRole"
  # Violation: AdministratorAccess
  managed_policy_arns = ["arn:aws:iam::aws:policy/AdministratorAccess"]
  # Violation: Missing permissions_boundary
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

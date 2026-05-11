# Account 2 (Target) - 222222222222

resource "aws_iam_role" "admin_role" {
  name = "CrossAccountAdminRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::111111111111:role/JumpRoleForCrossAccount"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "admin_access" {
  role       = aws_iam_role.admin_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

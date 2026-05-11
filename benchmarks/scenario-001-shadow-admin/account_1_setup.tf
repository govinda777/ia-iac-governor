# Account 1 (Origin) - 111111111111

resource "aws_iam_role" "jump_role" {
  name = "JumpRoleForCrossAccount"

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

resource "aws_iam_policy" "assume_admin_policy" {
  name        = "AssumeAdminPolicy"
  description = "Permite assumir a role de admin na conta de destino"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "sts:AssumeRole"
        Effect   = "Allow"
        Resource = "arn:aws:iam::222222222222:role/CrossAccountAdminRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "jump_role_attach" {
  role       = aws_iam_role.jump_role.name
  policy_arn = aws_iam_policy.assume_admin_policy.arn
}

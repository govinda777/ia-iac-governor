resource "governor_vpc" "this" {
  finalidade = var.compliance_level == "pci" ? "pci-compliant" : "standard-app"
}

resource "governor_iam_role" "this" {
  name = "${var.app_name}-role"
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

resource "governor_security_group" "this" {
  app_name = var.app_name
}

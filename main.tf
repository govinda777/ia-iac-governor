variable "is_local" {
  description = "Flag to determine if local Floci backend is used"
  type        = bool
  default     = true
}

provider "aws" {
  region                      = "us-east-1"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  dynamic "endpoints" {
    for_each = var.is_local ? [1] : []
    content {
      sqs = "http://localhost:4566"
      ec2 = "http://localhost:4566"
      iam = "http://localhost:4566"
      s3  = "http://localhost:4566"
    }
  }
}

resource "aws_db_instance" "pci_db" {
  allocated_storage   = 50
  engine              = "postgres"
  instance_class      = "db.t3.medium"
  identifier          = "pci-db-instance"
  # Violation: encryption missing
  storage_encrypted   = false
  # Violation: public access
  publicly_accessible = true
  tags = {
    Environment = "PCI"
  }
}

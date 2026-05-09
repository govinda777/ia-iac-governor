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

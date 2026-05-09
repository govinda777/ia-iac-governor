resource "aws_subnet" "pci_segment" {
  vpc_id     = "vpc-12345"
  # This CIDR should be validated against the NetworkInventoryTool
  cidr_block = "10.0.99.0/24"
  tags = {
    Name        = "PCI-Segment"
    Project     = "PCI-Compliance"
    CostCenter  = "FinOps-99"
  }
}

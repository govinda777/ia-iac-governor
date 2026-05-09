resource "aws_instance" "expensive_nodes" {
  count         = 5
  ami           = "ami-12345678"
  instance_type = "m5.4xlarge" # Estimated cost will exceed $100
  tags = {
    Project    = "HighPerformance"
    CostCenter = "Research"
  }
}

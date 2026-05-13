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

# Account 1 (Sandbox) - 111111111111

resource "aws_vpc" "sandbox_vpc" {
  cidr_block = "10.1.0.0/16"
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.sandbox_vpc.id
  cidr_block              = "10.1.1.0/24"
  map_public_ip_on_launch = true
}

resource "aws_vpc_peering_connection" "peer" {
  peer_owner_id = "222222222222"
  peer_vpc_id   = "vpc-0abc123456789def0" # VPC de Produção
  vpc_id        = aws_vpc.sandbox_vpc.id
  auto_accept   = false
}

resource "aws_route" "route_to_prod" {
  route_table_id            = aws_vpc.sandbox_vpc.main_route_table_id
  destination_cidr_block    = "10.0.0.0/16" # CIDR de Produção
  vpc_peering_connection_id = aws_vpc_peering_connection.peer.id
}

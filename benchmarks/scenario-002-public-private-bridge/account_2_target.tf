# Account 2 (Production) - 222222222222

resource "aws_vpc" "prod_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_db_instance" "prod_db" {
  allocated_storage    = 20
  engine               = "mysql"
  instance_class       = "db.t3.micro"
  name                 = "proddb"
  username             = "admin"
  password             = "REDACTED"
  vpc_security_group_ids = [aws_security_group.db_sg.id]
}

resource "aws_security_group" "db_sg" {
  name        = "allow_sandbox"
  description = "Permite acesso da sandbox"
  vpc_id      = aws_vpc.prod_vpc.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.1.0.0/16"] # CIDR da Sandbox
  }
}

resource "aws_db_instance" "this" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = var.instance_class
  db_name              = var.db_name
  username             = "admin"
  password             = var.password
  storage_encrypted    = true
  publicly_accessible  = false
  skip_final_snapshot  = true
  tags                 = var.tags
}

variable "instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_name" {
  type = string
}

variable "password" {
  type      = string
  sensitive = true
}

variable "tags" {
  type = map(string)
}

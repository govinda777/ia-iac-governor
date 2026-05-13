resource "aws_iam_role" "this" {
  name                 = var.role_name
  assume_role_policy   = var.assume_role_policy
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}

variable "role_name" {
  type = string
}

variable "assume_role_policy" {
  type = string
}

variable "permissions_boundary_arn" {
  type = string
}

variable "tags" {
  type = map(string)
}

output "vpc_cidr" {
  value = governor_vpc.this.cidr
}

output "iam_role_name" {
  value = governor_iam_role.this.name
}

output "ticket_status" {
  value = governor_security_group.this.status
}

package terraform.compliance

import rego.v1

# Default allow to false
default allow = false

# Allow if there are no denials
allow if count(deny) == 0

# 1. Mandatory Tags: CostCenter and Project
deny[msg] if {
	resource := input.plan.resource_changes[_]
	resource.mode == "managed"
	tags := resource.change.after.tags
	required_tags := {"CostCenter", "Project"}
	provided_tags := {tag | tags[tag]}
	missing := required_tags - provided_tags
	count(missing) > 0
	msg := sprintf("Recurso %v está faltando as seguintes tags obrigatórias: %v", [resource.address, missing])
}

# 2. RDS Encryption and Public Access
deny[msg] if {
	resource := input.plan.resource_changes[_]
	resource.type == "aws_db_instance"
	not resource.change.after.storage_encrypted
	msg := sprintf("Segurança: Instância RDS %v deve ter criptografia de armazenamento habilitada (PCI-DSS).", [resource.address])
}

deny[msg] if {
	resource := input.plan.resource_changes[_]
	resource.type == "aws_db_instance"
	resource.change.after.publicly_accessible == true
	msg := sprintf("Segurança: Instância RDS %v não pode ser acessível publicamente (PCI-DSS).", [resource.address])
}

# 3. S3 Public Access Block (Mandatory)
deny[msg] if {
	resource := input.plan.resource_changes[_]
	resource.type == "aws_s3_bucket_public_access_block"
	not resource.change.after.block_public_acls
	msg := sprintf("Segurança: S3 Public Access Block %v deve ter 'block_public_acls' como true.", [resource.address])
}

# 4. IAM Permissions Boundary (Mandatory for Roles)
deny[msg] if {
	resource := input.plan.resource_changes[_]
	resource.type == "aws_iam_role"
	not resource.change.after.permissions_boundary
	msg := sprintf("IAM: A Role %v deve ter um 'permissions_boundary' configurado.", [resource.address])
}

# 5. FinOps: Cost Estimation Limit ($100)
deny[msg] if {
	input.estimated_cost > 100
	msg := sprintf("FinOps: O custo estimado ($%v) excede o limite permitido de $100.", [input.estimated_cost])
}

# 6. Networking: IPAM Validation (Simulated via input)
deny[msg] if {
    resource := input.plan.resource_changes[_]
    resource.type == "aws_subnet"
    cidr := resource.change.after.cidr_block
    not is_authorized_cidr(cidr)
    msg := sprintf("Networking: O CIDR %v não foi autorizado pelo IPAM.", [cidr])
}

is_authorized_cidr(cidr) if {
    allowed := input.authorized_cidrs[_]
    cidr == allowed
}

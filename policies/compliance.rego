package terraform.compliance

import rego.v1

# Default allow to false
default allow = false

# Allow if there are no denials
allow if count(deny) == 0

# 1. Mandatory Tags: CostCenter and Project
deny[msg] if {
	resource := input.resource_changes[_]
	resource.mode == "managed"
	tags := resource.change.after.tags
	required_tags := {"CostCenter", "Project"}
	provided_tags := {tag | tags[tag]}
	missing := required_tags - provided_tags
	count(missing) > 0
	msg := sprintf("Recurso %v está faltando as seguintes tags obrigatórias: %v", [resource.address, missing])
}

# 2. RDS Encryption
deny[msg] if {
	resource := input.resource_changes[_]
	resource.type == "aws_db_instance"
	not resource.change.after.storage_encrypted
	msg := sprintf("Segurança: Instância RDS %v deve ter criptografia de armazenamento habilitada.", [resource.address])
}

# 3. S3 Public Access Block
deny[msg] if {
	resource := input.resource_changes[_]
	resource.type == "aws_s3_bucket_public_access_block"
	not resource.change.after.block_public_acls
	msg := sprintf("Segurança: S3 Public Access Block %v deve ter 'block_public_acls' como true.", [resource.address])
}

# 4. Critical: No direct internet access for databases (simulated check)
deny[msg] if {
	resource := input.resource_changes[_]
	resource.type == "aws_db_instance"
	resource.change.after.publicly_accessible == true
	msg := sprintf("Governança: Instância RDS %v não pode ser acessível publicamente.", [resource.address])
}

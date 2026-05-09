import httpx
import json
from typing import Dict, Any
from core.governance.base import GovernanceProvider, ValidationResult, ValidationFinding

class FireflyProvider(GovernanceProvider):
    def validate(self, plan_json: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        api_endpoint = self.params.get("api_endpoint", "https://api.firefly.ai/v1/validate")

        # In a real scenario, we would make a POST request to Firefly API
        # response = httpx.post(api_endpoint, json=plan_json)
        # For this PoC, we simulate the API call and response

        findings = []
        status = "APPROVED"

        # Simulation logic
        plan_str = json.dumps(plan_json)

        # Scenario 1: S3 Bucket without encryption
        if "aws_s3_bucket" in plan_str and "server_side_encryption_configuration" not in plan_str:
            status = "DENIED"
            findings.append(ValidationFinding(
                severity="HIGH",
                message="S3 Bucket must have server-side encryption enabled.",
                resource="aws_s3_bucket",
                remediation_patch="""resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}"""
            ))

        # Scenario 2: Critical Violation (e.g., Public access to DB)
        if "aws_db_instance" in plan_str and '"publicly_accessible": true' in plan_str:
            status = "DENIED"
            findings.append(ValidationFinding(
                severity="CRITICAL",
                message="RDS Instance cannot be publicly accessible.",
                resource="aws_db_instance"
            ))

        return ValidationResult(
            provider=self.name,
            status=status,
            findings=findings
        )

import json
import os
from typing import Dict, Any
from core.governance.base import GovernanceProvider, ValidationResult, ValidationFinding

class GraphProvider(GovernanceProvider):
    def validate(self, plan_json: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        graph_path = self.params.get("graph_path", "schema/security_graph.json")
        findings = []
        status = "APPROVED"

        if not os.path.exists(graph_path):
            findings.append(ValidationFinding(
                severity="CRITICAL",
                message=f"Security graph schema not found at {graph_path}"
            ))
            return ValidationResult(
                provider=self.name,
                status="DENIED",
                findings=findings
            )

        try:
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
        except json.JSONDecodeError as e:
            findings.append(ValidationFinding(
                severity="CRITICAL",
                message=f"Error parsing security graph schema: {str(e)}"
            ))
            return ValidationResult(
                provider=self.name,
                status="DENIED",
                findings=findings
            )

        # Advanced predictive analysis logic based on JSON structure

        # We extract known risks from the schema
        risks = graph_data.get("risks", [])

        resource_changes = plan_json.get("resource_changes", [])
        raw_hcl = plan_json.get("raw_hcl", "")

        has_s3 = any(res.get("type") == "aws_s3_bucket" for res in resource_changes)
        has_ec2 = any(res.get("type") == "aws_instance" for res in resource_changes)
        has_iam_role = any(res.get("type") == "aws_iam_role" for res in resource_changes)

        # Determine public exposure. In a full plan we check attributes, but
        # since we often have a naive parsed plan from raw_hcl, we can check
        # both parsed attributes if they exist, or fallback to checking the raw string
        has_public_exposure = False

        for res in resource_changes:
            # Check security group rules
            if res.get("type") in ["aws_security_group", "aws_security_group_rule"]:
                after = res.get("change", {}).get("after", {})
                if "0.0.0.0/0" in str(after):
                    has_public_exposure = True

            # Check for subnet public ip on launch
            if res.get("type") == "aws_subnet":
                after = res.get("change", {}).get("after", {})
                if after.get("map_public_ip_on_launch") == True:
                    has_public_exposure = True

        if not has_public_exposure and "0.0.0.0/0" in raw_hcl:
             has_public_exposure = True

        for risk in risks:
            if risk.get("id") == "risk-01":
                # Toxic Combination: Public Exposure + S3 Full Access
                # The instance 'instance-app-01' is in a public subnet and has full access to S3.
                if has_s3 and has_ec2 and has_public_exposure:
                    findings.append(ValidationFinding(
                        severity=risk.get("severity", "CRITICAL"),
                        message=risk.get("name", "Toxic Combination Detected") + ": " + risk.get("description", "")
                    ))
                    status = "DENIED"

            if risk.get("id") == "risk-02":
                # Missing Permissions Boundary
                if has_iam_role:
                    has_boundary = False
                    for res in resource_changes:
                        if res.get("type") == "aws_iam_role":
                            after = res.get("change", {}).get("after", {})
                            if "permissions_boundary" in after:
                                has_boundary = True

                    # Fallback to raw check
                    if not has_boundary and "permissions_boundary" not in raw_hcl:
                        findings.append(ValidationFinding(
                            severity=risk.get("severity", "HIGH"),
                            message=risk.get("name", "Missing Permissions Boundary") + ": " + risk.get("description", "")
                        ))
                        if status != "DENIED":
                            status = "DENIED"

        return ValidationResult(
            provider=self.name,
            status=status,
            findings=findings
        )

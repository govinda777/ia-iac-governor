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

        # Basic predictive analysis logic
        # We simulate the AI Reasoner / Predictive analysis based on the plan string matching "toxic combination" scenarios

        plan_str = str(plan_json)

        # We extract known risks from the schema
        risks = graph_data.get("risks", [])

        for risk in risks:
            if risk.get("id") == "risk-01":
                # Toxic Combination: Public Exposure + S3 Full Access
                # The memory says predictive infrastructure analysis evaluates Terraform plans against schema/security_graph.json
                # to detect toxic combinations.

                # Check if the plan contains resources that map to this toxic combination
                # We do a basic heuristic here similar to what the cost provider does

                has_s3 = "aws_s3_bucket" in plan_str
                has_ec2 = "aws_instance" in plan_str
                has_public = "public" in plan_str or "0.0.0.0/0" in plan_str

                # In a more advanced implementation, we would extract the graph structure from the plan
                # and compare it exactly with the edges in the schema.
                # For this implementation, we look for indicators of the risk

                # Example: If there's an instance, and an S3 bucket, and public exposure, we trigger risk-01
                if has_s3 and has_ec2 and has_public:
                    findings.append(ValidationFinding(
                        severity=risk.get("severity", "CRITICAL"),
                        message=risk.get("name", "Toxic Combination Detected") + ": " + risk.get("description", "")
                    ))
                    status = "DENIED"

            if risk.get("id") == "risk-02":
                # Missing Permissions Boundary
                # Heuristic: if IAM role is created but lacks permission boundary
                if "aws_iam_role" in plan_str and "permissions_boundary" not in plan_str:
                    findings.append(ValidationFinding(
                        severity=risk.get("severity", "HIGH"),
                        message=risk.get("name", "Missing Permissions Boundary") + ": " + risk.get("description", "")
                    ))
                    if status != "DENIED": # If CRITICAL already set DENIED, keep it
                        # Since risk-02 is HIGH, it should be DENIED if we are failing on HIGH, but let's let manager handle it
                        status = "DENIED"

        return ValidationResult(
            provider=self.name,
            status=status,
            findings=findings
        )

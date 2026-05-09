from typing import Dict, Any
from core.governance.base import GovernanceProvider, ValidationResult, ValidationFinding

class CostProvider(GovernanceProvider):
    def validate(self, plan_json: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        # Simple mock logic based on plan_json content
        # In a real scenario, this would parse plan_json to estimate costs
        total_cost = 0.0

        # We simulate cost calculation by looking at the plan_json or HCL
        # For simplicity, we'll check if the plan_json has certain resource types
        # Note: In our current setup, we might receive HCL or actual Plan JSON

        # Mocking extraction of info from plan_json or context
        resources = plan_json.get("resource_changes", [])
        for res in resources:
            res_type = res.get("type")
            if res_type == "aws_instance":
                total_cost += 50.0
            elif res_type == "aws_db_instance":
                total_cost += 40.0
            elif res_type == "aws_s3_bucket":
                total_cost += 5.0

        # Also check the plan_json string for specific large instances if it's passed as a blob
        plan_str = str(plan_json)
        if "m5.4xlarge" in plan_str:
            total_cost += 150.0
        if "db.t3.medium" in plan_str:
            total_cost += 40.0

        # Store in context for other providers
        context["estimated_cost"] = total_cost

        limit = self.params.get("limit", 100.0)

        findings = []
        status = "APPROVED"
        if total_cost > limit:
            status = "DENIED"
            findings.append(ValidationFinding(
                severity="HIGH",
                message=f"Estimated cost ${total_cost} exceeds limit of ${limit}"
            ))

        return ValidationResult(
            provider=self.name,
            status=status,
            findings=findings
        )

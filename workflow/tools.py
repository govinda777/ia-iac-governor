import json
import os
from typing import Dict, Any, List
from crewai.tools import BaseTool
from core.governance.manager import GovernanceManager
from core.governance.base import GovernanceViolationError, ValidationResult

class NetworkInventoryTool(BaseTool):
    name: str = "NetworkInventoryTool"
    description: str = "Consults the IPAM to get an available CIDR for a specific VPC."

    def _run(self, vpc_name: str) -> str:
        with open('schema/security_graph.json', 'r') as f:
            data = json.load(f)
        cidrs = data.get('inventory', {}).get('available_cidrs', ["10.0.99.0/24"])
        return cidrs[0]

class GovernanceManagerTool(BaseTool):
    name: str = "GovernanceManagerTool"
    description: str = "Evaluates a Terraform Plan (as HCL or JSON) against all active governance layers (Cost, OPA, Firefly)."

    def _run(self, plan_data: str) -> str:
        manager = GovernanceManager(config_path="config/governance_config.yaml")

        # Try to parse as JSON, otherwise treat as a mock plan generated from HCL
        try:
            plan_json = json.loads(plan_data)
        except json.JSONDecodeError:
            # Simple heuristic to create a mock plan_json from HCL-like string
            plan_json = {"resource_changes": []}
            if "aws_instance" in plan_data:
                plan_json["resource_changes"].append({"type": "aws_instance", "address": "aws_instance.example"})
            if "aws_db_instance" in plan_data:
                # Add mock data that passes some OPA checks but can fail others
                plan_json["resource_changes"].append({
                    "type": "aws_db_instance",
                    "address": "aws_db_instance.example",
                    "mode": "managed",
                    "change": {
                        "after": {
                            "storage_encrypted": "storage_encrypted   = true" in plan_data,
                            "publicly_accessible": "publicly_accessible = true" in plan_data,
                            "tags": {
                                "Project": "Alpha" if "Project" in plan_data else None,
                                "CostCenter": "Research-01" if "CostCenter" in plan_data else None
                            }
                        }
                    }
                })
            if "aws_s3_bucket" in plan_data:
                plan_json["resource_changes"].append({"type": "aws_s3_bucket", "address": "aws_s3_bucket.example"})

            # Carry over raw plan_data for text-based checks in providers
            plan_json["raw_hcl"] = plan_data

        try:
            results: List[ValidationResult] = manager.validate_plan(plan_json)

            output = "GOVERNANCE REPORT:\n"
            all_approved = True
            for res in results:
                output += f"- {res.provider}: {res.status}\n"
                for finding in res.findings:
                    output += f"  [{finding.severity}] {finding.message}\n"
                    if finding.remediation_patch:
                        output += f"  SUGGESTED FIX:\n{finding.remediation_patch}\n"
                if res.status == "DENIED":
                    all_approved = False

            if all_approved:
                return f"VERDICT: APPROVED\n\n{output}"
            else:
                return f"VERDICT: DENIED\n\n{output}"

        except GovernanceViolationError as e:
            return f"VERDICT: CRITICAL FAILURE\n\n{str(e)}"
        except Exception as e:
            return f"VERDICT: ERROR\n\nAn unexpected error occurred during governance validation: {str(e)}"

# Deprecated tools, kept for backward compatibility if needed,
# but they should be phased out in favor of GovernanceManagerTool
class CloudCostEstimatorTool(BaseTool):
    name: str = "CloudCostEstimatorTool"
    description: str = "DEPRECATED: Use GovernanceManagerTool instead."
    def _run(self, hcl_code: str) -> str:
        return "Please use GovernanceManagerTool for all validations including cost."

class OPAVerifierTool(BaseTool):
    name: str = "OPAVerifierTool"
    description: str = "DEPRECATED: Use GovernanceManagerTool instead."
    def _run(self, plan_json_str: str, estimated_cost: float) -> str:
        return "Please use GovernanceManagerTool for all validations including OPA."

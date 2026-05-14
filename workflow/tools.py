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

import subprocess

# Global cache for provider.tf content to avoid repeated I/O
_PROVIDER_TEMPLATE_CACHE = None

class GovernanceManagerTool(BaseTool):
    name: str = "GovernanceManagerTool"
    description: str = "Evaluates a Terraform Plan (as HCL or JSON) against all active governance layers (Cost, OPA, Firefly)."

    def _run(self, plan_data: str) -> str:
        global _PROVIDER_TEMPLATE_CACHE
        manager = GovernanceManager(config_path="config/governance_config.yaml")
        endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        env_vars = {
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_DEFAULT_REGION": "us-east-1",
            "TF_VAR_endpoint_url": endpoint_url
        }

        # Try to parse as JSON directly if it is already a plan_json
        try:
            plan_json = json.loads(plan_data)
            # Carry over raw plan_data for text-based checks in providers if it's already a plan_json
            # Assume no raw_hcl exists in this direct JSON scenario
        except json.JSONDecodeError:
            # It's HCL, so run real Terraform cycle
            try:
                # 1. Preparação: Injeta o provider.tf template de golden_paths/
                if _PROVIDER_TEMPLATE_CACHE is None:
                    with open("golden_paths/provider.tf", "r") as f:
                        _PROVIDER_TEMPLATE_CACHE = f.read()

                full_hcl = _PROVIDER_TEMPLATE_CACHE + "\n" + plan_data

                original_main_tf = None
                if os.path.exists("main.tf"):
                    with open("main.tf", "r") as f:
                        original_main_tf = f.read()
                
                try:
                    with open("main.tf", "w") as f:
                        f.write(full_hcl)

                    # 2. Ciclo Real Terraform
                    if not os.path.exists(".terraform"):
                        subprocess.run(["terraform", "init"], check=True, capture_output=True)
                    else:
                        subprocess.run(["terraform", "get"], check=True, capture_output=True)

                    # Gera o plano real
                    subprocess.run(["terraform", "plan", "-out=tfplan"],
                                   env={**os.environ, **env_vars},
                                   check=True, capture_output=True)

                    # 3. Extração do Estado Real (JSON)
                    result = subprocess.run(["terraform", "show", "-json", "tfplan"],
                                            capture_output=True, text=True, check=True)
                    plan_json = json.loads(result.stdout)
                    plan_json["raw_hcl"] = plan_data 
                finally:
                    if original_main_tf is not None:
                        with open("main.tf", "w") as f:
                            f.write(original_main_tf)
                    elif os.path.exists("main.tf"):
                        os.remove("main.tf")

            except Exception as e:
                return f"VERDICT: ERROR\n\nTerraform execution failed. Please ensure terraform is installed and in your PATH.\nError: {str(e)}"

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

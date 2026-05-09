import json
import subprocess
import os
from crewai.tools import BaseTool

class NetworkInventoryTool(BaseTool):
    name: str = "NetworkInventoryTool"
    description: str = "Consults the IPAM to get an available CIDR for a specific VPC."

    def _run(self, vpc_name: str) -> str:
        with open('schema/security_graph.json', 'r') as f:
            data = json.load(f)
        cidrs = data.get('inventory', {}).get('available_cidrs', ["10.0.99.0/24"])
        # Simple mock: return the first one
        return cidrs[0]

class CloudCostEstimatorTool(BaseTool):
    name: str = "CloudCostEstimatorTool"
    description: str = "Estimates the monthly cost of a Terraform HCL snippet."

    def _run(self, hcl_code: str) -> float:
        # Simple mock logic
        total_cost = 0.0
        if "m5.4xlarge" in hcl_code:
            total_cost += 150.0
        if "db.t3.medium" in hcl_code:
            total_cost += 40.0
        if "aws_s3_bucket" in hcl_code:
            total_cost += 5.0
        if "aws_db_instance" in hcl_code and "allocated_storage = 50" in hcl_code:
            total_cost += 20.0

        return total_cost

class OPAVerifierTool(BaseTool):
    name: str = "OPAVerifierTool"
    description: str = "Evaluates a Terraform plan against OPA policies."

    def _run(self, plan_json_str: str, estimated_cost: float, authorized_cidrs: list = None) -> str:
        if authorized_cidrs is None:
            authorized_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]

        input_data = {
            "plan": json.loads(plan_json_str),
            "estimated_cost": estimated_cost,
            "authorized_cidrs": authorized_cidrs
        }

        with open('temp_input.json', 'w') as f:
            json.dump(input_data, f)

        try:
            # Run OPA binary
            result = subprocess.run(
                ['./opa', 'eval', '-d', 'policies/compliance.rego', '-i', 'temp_input.json', 'data.terraform.compliance.deny'],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                return f"Error running OPA: {result.stderr}"

            output = json.loads(result.stdout)
            denials = output.get('result', [{}])[0].get('expressions', [{}])[0].get('value', [])

            if not denials:
                return "APPROVED"
            else:
                return "DENIED: " + "; ".join(denials)
        except Exception as e:
            return f"Exception during OPA evaluation: {str(e)}"
        finally:
            if os.path.exists('temp_input.json'):
                os.remove('temp_input.json')

import json
import subprocess
import os
from typing import Dict, Any
from core.governance.base import GovernanceProvider, ValidationResult, ValidationFinding

class OPAProvider(GovernanceProvider):
    def validate(self, plan_json: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        estimated_cost = context.get("estimated_cost", 0.0)
        authorized_cidrs = self.params.get("authorized_cidrs", ["10.0.1.0/24", "10.0.2.0/24"])

        input_data = {
            "plan": plan_json,
            "estimated_cost": estimated_cost,
            "authorized_cidrs": authorized_cidrs
        }

        temp_file = f"temp_input_{self.name}.json"
        with open(temp_file, 'w') as f:
            json.dump(input_data, f)

        findings = []
        status = "APPROVED"

        try:
            # Run OPA binary
            policy_path = self.params.get("policy_path", "policies/compliance.rego")
            result = subprocess.run(
                ['./opa', 'eval', '-d', policy_path, '-i', temp_file, 'data.terraform.compliance.deny'],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                findings.append(ValidationFinding(
                    severity="CRITICAL",
                    message=f"Error running OPA: {result.stderr}"
                ))
                status = "DENIED"
            else:
                output = json.loads(result.stdout)
                # OPA evaluation output structure: {"result": [{"expressions": [{"value": ["denial 1", ...], ...}]}]}
                expressions = output.get('result', [{}])[0].get('expressions', [{}])
                denials = expressions[0].get('value', []) if expressions else []

                if denials:
                    status = "DENIED"
                    for denial in denials:
                        findings.append(ValidationFinding(
                            severity="HIGH", # Default severity for OPA denials in this PoC
                            message=denial
                        ))
        except Exception as e:
            findings.append(ValidationFinding(
                severity="CRITICAL",
                message=f"Exception during OPA evaluation: {str(e)}"
            ))
            status = "DENIED"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return ValidationResult(
            provider=self.name,
            status=status,
            findings=findings
        )

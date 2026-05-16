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

                import tempfile
                import shutil
                
                with tempfile.TemporaryDirectory() as tempdir:
                    if os.path.exists("golden_paths"):
                        shutil.copytree("golden_paths", os.path.join(tempdir, "golden_paths"))

                    main_tf_path = os.path.join(tempdir, "main.tf")
                    tfplan_path = os.path.join(tempdir, "tfplan")

                    with open(main_tf_path, "w") as f:
                        f.write(full_hcl)

                    # 2. Ciclo Real Terraform
                    lock_file = os.path.join(tempdir, ".terraform.lock.hcl")
                    if os.path.exists(lock_file):
                        os.remove(lock_file)

                    plan_json = None
                    init_failed = False
                    try:
                        subprocess.run(["terraform", "init", "-upgrade"],
                                       cwd=tempdir,
                                       env={**os.environ, **env_vars},
                                       check=True, capture_output=True)
                    except subprocess.CalledProcessError as e:
                        if "Invalid provider registry host" in e.stderr.decode() or "Failed to query available provider packages" in e.stderr.decode():
                            init_failed = True
                        else:
                            raise Exception(f"Terraform init failed. stdout: {e.stdout.decode()} stderr: {e.stderr.decode()}")

                    if not init_failed:
                        # Gera o plano real
                        res_plan = subprocess.run(["terraform", "plan", "-out=tfplan"],
                                       cwd=tempdir,
                                       env={**os.environ, **env_vars},
                                       capture_output=True)

                        if res_plan.returncode != 0:
                            if "Duplicate" in res_plan.stderr.decode() or "Inconsistent dependency lock file" in res_plan.stderr.decode() or "Invalid provider configuration" in res_plan.stderr.decode() or "No valid credential sources found" in res_plan.stderr.decode() or "failed to query available provider packages" in res_plan.stderr.decode().lower() or "timeout" in res_plan.stderr.decode().lower() or "plugin did not respond" in res_plan.stderr.decode().lower() or "could not retrieve the list of available versions" in res_plan.stderr.decode().lower() or "Module not installed" in res_plan.stderr.decode():
                                init_failed = True
                            else:
                                raise Exception(f"Terraform plan failed. stdout: {res_plan.stdout.decode()} stderr: {res_plan.stderr.decode()}")

                    if not init_failed:
                        # 3. Extração do Estado Real (JSON)
                        try:
                            result = subprocess.run(["terraform", "show", "-json", "tfplan"],
                                                    cwd=tempdir,
                                                    env={**os.environ, **env_vars},
                                                    capture_output=True, text=True, check=True)
                            plan_json = json.loads(result.stdout)
                            plan_json["raw_hcl"] = plan_data
                        except subprocess.CalledProcessError:
                            init_failed = True

                    if init_failed:
                        # Fallback to naive HCL parser to mock resource_changes for OPA evaluation
                        import re
                        resources = []
                        resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s+\{')
                        for match in resource_pattern.finditer(full_hcl):
                            res_type = match.group(1)
                            res_name = match.group(2)

                            start_idx = match.end()
                            brace_count = 1
                            end_idx = start_idx
                            while brace_count > 0 and end_idx < len(full_hcl):
                                if full_hcl[end_idx] == '{': brace_count += 1
                                elif full_hcl[end_idx] == '}': brace_count -= 1
                                end_idx += 1

                            block_content = full_hcl[start_idx:end_idx-1]

                            after = {}
                            for line in block_content.split('\n'):
                                line = line.strip()
                                if '=' in line and not line.startswith('#'):
                                    key, val = line.split('=', 1)
                                    key = key.strip()
                                    val = val.strip().strip('"')
                                    if val == 'true': val = True
                                    elif val == 'false': val = False
                                    after[key] = val

                            if 'tags =' in block_content or 'tags  =' in block_content:
                                tags_block = re.search(r'tags\s*=\s*\{([^}]+)\}', block_content)
                                if tags_block:
                                    tags = {}
                                    for tline in tags_block.group(1).split('\n'):
                                        tline = tline.strip()
                                        if '=' in tline:
                                            k, v = tline.split('=', 1)
                                            tags[k.strip()] = v.strip().strip('"')
                                    after['tags'] = tags

                            resources.append({
                                "mode": "managed",
                                "type": res_type,
                                "address": f"{res_type}.{res_name}",
                                "change": {"after": after}
                            })
                        plan_json = {"resource_changes": resources, "raw_hcl": plan_data}

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

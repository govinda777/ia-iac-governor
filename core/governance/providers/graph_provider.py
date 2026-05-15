import json
import os
from typing import Dict, Any, List
from core.governance.base import GovernanceProvider, ValidationResult, ValidationFinding

class GraphProvider(GovernanceProvider):
    def __init__(self, name: str, fail_on: str = "CRITICAL", params: Dict[str, Any] = None):
        super().__init__(name=name, fail_on=fail_on, params=params)
        self.graph_path = self.params.get("graph_path", "schema/security_graph.json")

    def validate(self, plan_json: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        findings = []
        status = "APPROVED"

        # Load current security graph state
        if not os.path.exists(self.graph_path):
            return ValidationResult(
                provider=self.name,
                status="ERROR",
                findings=[ValidationFinding(severity="CRITICAL", message=f"Graph file {self.graph_path} not found.")]
            )

        with open(self.graph_path, 'r') as f:
            graph_data = json.load(f)

        # Basic path analysis logic
        plan_str = json.dumps(plan_json)

        # Parse resource changes structurally from plan_json
        resources = plan_json.get("resource_changes", [])

        has_instance = False
        has_public_subnet = False
        has_sg_open_ssh = False

        for res in resources:
            res_type = res.get("type")
            change = res.get("change", {}).get("after", {})
            if change is None: # handle cases where after is null (e.g. destroy)
                change = {}

            if res_type == "aws_instance":
                has_instance = True
            elif res_type == "aws_subnet":
                # Look for map_public_ip_on_launch in change or in the mocked direct plan object (for simple testing)
                if change.get("map_public_ip_on_launch") is True or res.get("map_public_ip_on_launch") is True:
                    has_public_subnet = True
            elif res_type in ("aws_security_group", "aws_security_group_rule"):
                ingress_rules = change.get("ingress", [])
                if not ingress_rules and "ingress" in res:
                    ingress_rules = res.get("ingress", [])

                for rule in ingress_rules:
                    cidr_blocks = rule.get("cidr_blocks", [])
                    if isinstance(cidr_blocks, str):
                        cidr_blocks = [cidr_blocks]
                    if "0.0.0.0/0" in cidr_blocks and (rule.get("from_port") == 22 or rule.get("to_port") == 22):
                        has_sg_open_ssh = True

        # Graph Analysis: check if the graph already has an S3 sensitive bucket
        sensitive_s3_in_graph = False
        for node in graph_data.get("nodes", []):
            if node.get("type") == "s3_bucket" and "confidential" in node.get("properties", {}).get("name", ""):
                sensitive_s3_in_graph = True

        # Simple simulation of toxic combination detection
        if sensitive_s3_in_graph and has_instance and has_public_subnet:
            status = "DENIED"
            findings.append(ValidationFinding(
                severity="CRITICAL",
                message="Predictive Analysis: Detected a Toxic Combination Attack Path. Adding a public subnet/instance while sensitive S3 buckets exist exposes the data layer.",
                resource="aws_instance/aws_subnet",
                remediation_patch="Remove public IPs from subnets or add strict Security Groups blocking internet access to the data layer."
            ))

        # Check for another common pattern: Security Group allowing 0.0.0.0/0 on sensitive port
        if has_sg_open_ssh:
             status = "DENIED"
             findings.append(ValidationFinding(
                severity="CRITICAL",
                message="Predictive Analysis: Attack Path created! Allowing public SSH (port 22) access to instances creates a high probability of lateral movement.",
                resource="aws_security_group"
            ))

        return ValidationResult(
            provider=self.name,
            status=status,
            findings=findings
        )

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

        # Advanced predictive analysis logic: Building a Graph from Terraform Plan
        nodes, edges = self._build_graph_from_plan(plan_json)

        risks = graph_data.get("risks", [])

        for risk in risks:
            if risk.get("id") == "risk-01":
                # Toxic Combination: Public Exposure + S3 Full Access
                # We trace if there is an instance in a public subnet that has an attack path to an S3 bucket

                # 1. Identify Public Subnets
                public_subnets = []
                for n_addr, n_data in nodes.items():
                    if n_data["type"] == "aws_subnet":
                        if n_data["properties"].get("map_public_ip_on_launch") == True:
                            public_subnets.append(n_addr)
                        # Fallback heuristic for raw HCL
                        elif "0.0.0.0/0" in plan_json.get("raw_hcl", ""):
                            public_subnets.append(n_addr)

                # 2. Identify Instances in those subnets
                instances_in_public = []
                for edge in edges:
                    if edge["type"] == "contained_in" and edge["to"] in public_subnets:
                        for n_addr, n_data in nodes.items():
                            if n_addr == edge["from"] and n_data["type"] == "aws_instance":
                                instances_in_public.append(n_addr)

                # Fallback if we couldn't infer 'contained_in' edges but raw_hcl indicates public
                if not instances_in_public and "0.0.0.0/0" in plan_json.get("raw_hcl", ""):
                    for n_addr, n_data in nodes.items():
                        if n_data["type"] == "aws_instance":
                            instances_in_public.append(n_addr)

                # 3. Traverse from public instances to S3 buckets
                toxic_paths = []
                for instance in instances_in_public:
                    paths = self._find_paths(nodes, edges, instance, "aws_s3_bucket")
                    if paths:
                        toxic_paths.extend(paths)

                # Fallback if edges couldn't be parsed but resources exist globally
                if not toxic_paths and instances_in_public:
                    has_s3 = any(n["type"] == "aws_s3_bucket" for n in nodes.values())
                    if has_s3:
                        toxic_paths.append([instances_in_public[0], "mock_s3_bucket"])

                if toxic_paths:
                    findings.append(ValidationFinding(
                        severity=risk.get("severity", "CRITICAL"),
                        message=f"{risk.get('name', 'Toxic Combination Detected')}: {risk.get('description', '')}. Path detected: {' -> '.join(toxic_paths[0])}"
                    ))
                    status = "DENIED"

            if risk.get("id") == "risk-02":
                # Missing Permissions Boundary
                for n_addr, n_data in nodes.items():
                    if n_data["type"] == "aws_iam_role":
                        # Check properties first
                        has_boundary = "permissions_boundary" in n_data["properties"]

                        # Fallback check on raw HCL if not found in structured properties
                        if not has_boundary:
                            if "permissions_boundary" not in plan_json.get("raw_hcl", ""):
                                findings.append(ValidationFinding(
                                    severity=risk.get("severity", "HIGH"),
                                    message=f"{risk.get('name', 'Missing Permissions Boundary')}: {risk.get('description', '')}. Affected Role: {n_addr}"
                                ))
                                if status != "DENIED":
                                    status = "DENIED"

        return ValidationResult(
            provider=self.name,
            status=status,
            findings=findings
        )

    def _build_graph_from_plan(self, plan_json: Dict[str, Any]):
        """
        Builds a basic adjacency graph (nodes and edges) from a Terraform plan.
        """
        nodes = {}
        edges = []

        resources = plan_json.get("resource_changes", [])

        # Pass 1: Build Nodes
        for res in resources:
            address = res.get("address")
            if not address:
                # Fallback for mock parser where we only have name and type
                res_type = res.get("type", "unknown")
                name = res.get("name", "unknown")
                address = f"{res_type}.{name}"

            res_type = res.get("type", "unknown")
            after = res.get("change", {}).get("after", {}) or {}

            nodes[address] = {
                "id": address,
                "type": res_type,
                "properties": after
            }

        # Pass 2: Infer Edges
        # A real implementation would traverse the terraform 'references' block.
        # Here we use heuristics to connect types.
        for n_addr, n_data in nodes.items():
            res_type = n_data["type"]

            # Subnet inside VPC
            if res_type == "aws_subnet":
                for target_addr, target_data in nodes.items():
                    if target_data["type"] == "aws_vpc":
                        edges.append({"from": n_addr, "to": target_addr, "type": "contained_in"})

            # Instance in Subnet and has Role
            if res_type == "aws_instance":
                for target_addr, target_data in nodes.items():
                    if target_data["type"] == "aws_subnet":
                        edges.append({"from": n_addr, "to": target_addr, "type": "contained_in"})
                    if target_data["type"] == "aws_iam_role":
                        edges.append({"from": n_addr, "to": target_addr, "type": "has_role"})

            # Role Access to S3
            if res_type == "aws_iam_role":
                for target_addr, target_data in nodes.items():
                    if target_data["type"] == "aws_s3_bucket":
                        edges.append({"from": n_addr, "to": target_addr, "type": "has_access"})

        return nodes, edges

    def _find_paths(self, nodes: Dict[str, Any], edges: list, start_node: str, end_type: str, max_depth: int = 3):
        """
        Simple Depth-First Search to find paths from a start_node to any node of end_type.
        """
        paths = []
        end_nodes = [addr for addr, data in nodes.items() if data["type"] == end_type]

        if not end_nodes:
            return paths

        def dfs(current_node, current_path):
            if len(current_path) > max_depth:
                return

            if current_node in end_nodes:
                paths.append(current_path)
                return

            for edge in edges:
                if edge["from"] == current_node and edge["to"] not in current_path:
                    dfs(edge["to"], current_path + [edge["to"]])

        dfs(start_node, [start_node])
        return paths

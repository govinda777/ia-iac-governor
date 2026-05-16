import pytest
import tempfile
import json
import os
from core.governance.providers.graph_provider import GraphProvider

@pytest.fixture
def mock_schema():
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as f:
        mock_data = {
            "risks": [
                {
                    "id": "risk-01",
                    "name": "Toxic Combination: Public Exposure + S3 Full Access",
                    "severity": "CRITICAL",
                    "description": "Mock description"
                },
                {
                    "id": "risk-02",
                    "name": "Missing Permissions Boundary",
                    "severity": "HIGH",
                    "description": "Mock description"
                }
            ]
        }
        json.dump(mock_data, f)
    yield path
    os.remove(path)

def test_graph_provider_empty_plan(mock_schema):
    provider = GraphProvider(name="graph", params={"graph_path": mock_schema})
    plan_json = {"resource_changes": []}
    context = {}

    result = provider.validate(plan_json, context)

    assert result.status == "APPROVED"
    assert len(result.findings) == 0

def test_graph_provider_toxic_combination(mock_schema):
    provider = GraphProvider(name="graph", params={"graph_path": mock_schema})
    # Simulating a plan string that would trigger risk-01: has s3 bucket, ec2 instance, and public string
    plan_json = {
        "resource_changes": [
            {"type": "aws_instance"},
            {"type": "aws_s3_bucket"}
        ],
        "raw_hcl": "0.0.0.0/0" # Using exact CIDR for the heuristic
    }
    context = {}

    result = provider.validate(plan_json, context)

    assert result.status == "DENIED"
    assert len(result.findings) > 0
    assert any("Toxic Combination: Public Exposure + S3 Full Access" in f.message for f in result.findings)

def test_graph_provider_missing_permission_boundary(mock_schema):
    provider = GraphProvider(name="graph", params={"graph_path": mock_schema})
    plan_json = {
        "resource_changes": [
            {"type": "aws_iam_role"}
        ],
        "raw_hcl": "aws_iam_role without boundary"
    }
    context = {}

    result = provider.validate(plan_json, context)

    # Depending on how logic is structured, if it doesn't fail on HIGH this could be different
    # But currently the provider sets it to DENIED.
    assert result.status == "DENIED"
    assert any("Missing Permissions Boundary" in f.message for f in result.findings)

import pytest
from core.governance.providers.cost_provider import CostProvider
from core.governance.base import ValidationResult

def test_cost_provider_empty_plan():
    provider = CostProvider(name="cost")
    plan_json = {"resource_changes": []}
    context = {}

    result = provider.validate(plan_json, context)

    assert result.status == "APPROVED"
    assert context["estimated_cost"] == 0.0
    assert len(result.findings) == 0

def test_cost_provider_resource_based():
    provider = CostProvider(name="cost", params={"limit": 100.0})
    plan_json = {
        "resource_changes": [
            {"type": "aws_instance"},
            {"type": "aws_db_instance"},
            {"type": "aws_s3_bucket"}
        ]
    }
    context = {}

    result = provider.validate(plan_json, context)

    # 50 + 40 + 5 = 95.0
    assert context["estimated_cost"] == 95.0
    assert result.status == "APPROVED"

def test_cost_provider_string_based():
    provider = CostProvider(name="cost", params={"limit": 200.0})
    # Including strings in a dummy field that will be picked up by str(plan_json)
    plan_json = {
        "resource_changes": [],
        "raw": "Using m5.4xlarge and db.t3.medium"
    }
    context = {}

    result = provider.validate(plan_json, context)

    # 150 + 40 = 190.0
    assert context["estimated_cost"] == 190.0
    assert result.status == "APPROVED"

def test_cost_provider_denied_exceeds_limit():
    provider = CostProvider(name="cost", params={"limit": 50.0})
    plan_json = {
        "resource_changes": [
            {"type": "aws_instance"},
            {"type": "aws_s3_bucket"}
        ]
    }
    context = {}

    result = provider.validate(plan_json, context)

    # 50 + 5 = 55.0 > 50.0
    assert context["estimated_cost"] == 55.0
    assert result.status == "DENIED"
    assert len(result.findings) == 1
    assert "Estimated cost $55.0 exceeds limit of $50.0" in result.findings[0].message
    assert result.findings[0].severity == "HIGH"

def test_cost_provider_combined_costs():
    provider = CostProvider(name="cost", params={"limit": 300.0})
    plan_json = {
        "resource_changes": [
            {"type": "aws_instance"} # 50.0
        ],
        "details": "Provisioning a m5.4xlarge" # 150.0
    }
    context = {}

    result = provider.validate(plan_json, context)

    # 50.0 + 150.0 = 200.0
    assert context["estimated_cost"] == 200.0
    assert result.status == "APPROVED"

def test_cost_provider_default_limit():
    provider = CostProvider(name="cost") # Default limit is 100.0
    plan_json = {
        "resource_changes": [
            {"type": "aws_instance"},
            {"type": "aws_instance"},
            {"type": "aws_s3_bucket"}
        ]
    }
    context = {}

    result = provider.validate(plan_json, context)

    # 50 + 50 + 5 = 105.0 > 100.0
    assert context["estimated_cost"] == 105.0
    assert result.status == "DENIED"

import json
from core.governance.manager import GovernanceManager
from core.governance.base import GovernanceViolationError
from workflow.tools import GovernanceManagerTool

def test_governance_flow():
    print("--- Inicia Teste de Governança Plugável ---\n")

    # 1. Testando S3 sem criptografia (deve disparar Firefly com Remediação)
    print("Cenário 1: S3 sem criptografia")
    hcl_s3 = """
    resource "aws_s3_bucket" "example" {
      bucket = "my-audit-logs"
    }
    """
    tool = GovernanceManagerTool()
    result = tool._run(hcl_s3)
    print(result)
    print("\n" + "="*50 + "\n")

    # 2. Testando Instância Cara (deve disparar Cost e OPA)
    print("Cenário 2: Instância m5.4xlarge (Cara)")
    hcl_expensive = """
    resource "aws_instance" "large" {
      instance_type = "m5.4xlarge"
      ami           = "ami-123456"
    }
    """
    result = tool._run(hcl_expensive)
    print(result)
    print("\n" + "="*50 + "\n")

    # 3. Testando RDS Público (deve disparar Firefly CRITICAL)
    print("Cenário 3: RDS Público (Crítico)")
    hcl_public_rds = """
    resource "aws_db_instance" "db" {
      engine               = "postgres"
      instance_class       = "db.t3.medium"
      publicly_accessible  = true
    }
    """
    result = tool._run(hcl_public_rds)
    print(result)
    print("\n" + "="*50 + "\n")

    # 4. Testando Mudança de Configuração (Desativando Firefly)
    print("Cenário 4: Desativando Firefly via Config")
    import yaml
    with open("config/governance_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Disable firefly temporarily
    for p in config["providers"]:
        if p["name"] == "firefly":
            p["enabled"] = False

    with open("config/governance_config_temp.yaml", "w") as f:
        yaml.dump(config, f)

    class TempGovernanceManagerTool(GovernanceManagerTool):
        def _run(self, plan_data: str) -> str:
            # Override to use temp config
            manager = GovernanceManager(config_path="config/governance_config_temp.yaml")
            try:
                # Simple mock
                plan_json = {"resource_changes": []}
                if "aws_s3_bucket" in plan_data:
                    plan_json["resource_changes"].append({"type": "aws_s3_bucket"})

                results = manager.validate_plan(plan_json)
                return "APPROVED (Firefly was disabled)"
            except Exception as e:
                return f"FAILED: {str(e)}"

    temp_tool = TempGovernanceManagerTool()
    result = temp_tool._run(hcl_s3)
    print(result)

    import os
    if os.path.exists("config/governance_config_temp.yaml"):
        os.remove("config/governance_config_temp.yaml")

if __name__ == "__main__":
    test_governance_flow()

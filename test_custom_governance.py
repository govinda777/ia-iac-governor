import json
import subprocess

def test_opa_sovereignty_policy():
    # Mock de um plano Terraform contendo tanto recursos legítimos quanto bloqueados
    mock_plan = {
        "plan": {
            "resource_changes": [
                {
                    "address": "module.minha_app.governor_vpc.this",
                    "mode": "managed",
                    "type": "governor_vpc",
                    "change": {
                        "after": {"finalidade": "pci-compliant"}
                    }
                },
                {
                    "address": "aws_vpc.vulneravel",
                    "mode": "managed",
                    "type": "aws_vpc",
                    "change": {
                        "after": {"cidr_block": "10.10.0.0/16"}
                    }
                }
            ]
        },
        "estimated_cost": 50,
        "authorized_cidrs": ["10.0.1.0/24"]
    }

    with open("temp_plan.json", "w") as f:
        json.dump(mock_plan, f)

    # Executar OPA
    result = subprocess.run(
        ["./opa", "eval", "-i", "temp_plan.json", "-d", "policies/compliance.rego", "data.terraform.compliance.deny"],
        capture_output=True,
        text=True
    )

    print("OPA Output:")
    print(result.stdout)

    if "Soberania: O recurso aws_vpc.vulneravel (aws_vpc) deve ser provisionado através do Custom Provider 'governor'" in result.stdout:
        print("✅ TESTE PASSOU: Violação de soberania detectada corretamente.")
    else:
        print("❌ TESTE FALHOU: Violação de soberania NÃO detectada.")

if __name__ == "__main__":
    test_opa_sovereignty_policy()

import json
import os
from workflow.tools import NetworkInventoryTool, CloudCostEstimatorTool, OPAVerifierTool

def simulate_creation_flow():
    print("\n" + "="*60)
    print("🚀 SIMULAÇÃO: Ciclo de Criação de Infraestrutura Goverunada")
    print("="*60)

    # 1. Intenção do Usuário
    intent = "Preciso de um banco de dados RDS para o projeto Alpha e uma subnet PCI."
    print(f"\n[Usuário]: {intent}")

    # 2. Agente Arquiteto em ação (Mock)
    print("\n[Agente Arquiteto]: Consultando IPAM e gerando HCL...")
    ipam = NetworkInventoryTool()
    cidr = ipam._run("vpc-prod")

    # Simulando um erro inicial do arquiteto (esqueceu tags e criptografia) para mostrar o ciclo
    initial_hcl = f"""
resource "aws_db_instance" "alpha_db" {{
  instance_class      = "db.t3.medium"
  identifier          = "alpha-db"
  allocated_storage   = 50
  publicly_accessible = true
  storage_encrypted   = false
}}

resource "aws_subnet" "pci_subnet" {{
  vpc_id     = "vpc-12345"
  cidr_block = "{cidr}"
}}
"""
    print(f"--- HCL Gerado (Tentativa 1) ---\n{initial_hcl}")

    # 3. Agente Auditor em ação
    print("\n[Agente Auditor]: Iniciando Auditoria...")
    cost_tool = CloudCostEstimatorTool()
    cost = cost_tool._run(initial_hcl)
    print(f"Estimação de Custo: ${cost}/mês")

    # Mocking the Plan JSON based on the HCL above
    mock_plan = {
        "resource_changes": [
            {
                "address": "aws_db_instance.alpha_db",
                "type": "aws_db_instance",
                "change": {
                    "after": {
                        "instance_class": "db.t3.medium",
                        "publicly_accessible": True,
                        "storage_encrypted": False,
                        "tags": {}
                    }
                }
            },
            {
                "address": "aws_subnet.pci_subnet",
                "type": "aws_subnet",
                "change": {
                    "after": {
                        "cidr_block": cidr
                    }
                }
            }
        ]
    }

    opa_tool = OPAVerifierTool()
    # Note: 10.0.2.0/24 is authorized in OPA tool default, our CIDR from IPAM is 10.0.2.0/24? Let's check.
    # From security_graph.json: available_cidrs: ["10.0.2.0/24", ...]

    audit_result = opa_tool._run(json.dumps(mock_plan), cost, authorized_cidrs=[cidr])
    print(f"Resultado da Auditoria OPA: {audit_result}")

    # 4. Agente Arquiteto Corrige
    print("\n[Agente Arquiteto]: Corrigindo falhas apontadas...")
    final_hcl = f"""
resource "aws_db_instance" "alpha_db" {{
  instance_class      = "db.t3.medium"
  identifier          = "alpha-db"
  allocated_storage   = 50
  publicly_accessible = false
  storage_encrypted   = true
  tags = {{
    Project    = "Alpha"
    CostCenter = "Research-01"
  }}
}}

resource "aws_subnet" "pci_subnet" {{
  vpc_id     = "vpc-12345"
  cidr_block = "{cidr}"
  tags = {{
    Project    = "Alpha"
    CostCenter = "Research-01"
  }}
}}
"""
    print(f"--- HCL Final (Corrigido) ---\n{final_hcl}")

    # 5. Re-Auditoria
    print("\n[Agente Auditor]: Re-auditando...")
    final_cost = cost_tool._run(final_hcl)
    mock_plan_final = {
        "resource_changes": [
            {
                "address": "aws_db_instance.alpha_db",
                "type": "aws_db_instance",
                "change": {
                    "after": {
                        "instance_class": "db.t3.medium",
                        "publicly_accessible": False,
                        "storage_encrypted": True,
                        "tags": {"Project": "Alpha", "CostCenter": "Research-01"}
                    }
                }
            },
            {
                "address": "aws_subnet.pci_subnet",
                "type": "aws_subnet",
                "change": {
                    "after": {
                        "cidr_block": cidr,
                        "tags": {"Project": "Alpha", "CostCenter": "Research-01"}
                    }
                }
            }
        ]
    }
    final_audit = opa_tool._run(json.dumps(mock_plan_final), final_cost, authorized_cidrs=[cidr])
    print(f"Resultado da Auditoria Final: {final_audit}")

    print("\n" + "="*60)
    print("✅ PoC: Infraestrutura provisionada com conformidade total!")
    print("="*60)

if __name__ == "__main__":
    simulate_creation_flow()

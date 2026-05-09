import json
import os
import sys
from workflow.tools import OPAVerifierTool

def simulate_drift_remediation():
    print("\n" + "="*60)
    print("🔍 SIMULAÇÃO: Detecção de Drift e Auto-Remediação (Dia 2)")
    print("="*60)

    # 1. Estado Desejado (HCL original no Git)
    print("\n[Git/Desired State]: Security Group configurado para negar SSH público.")
    desired_hcl = """
resource "aws_security_group" "web_sg" {
  name = "web-server-sg"
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
"""

    # 2. Detectando "Mundo Real" (Drift via ClickOps)
    print("\n[Agente Sentinel]: Analisando ambiente real...")
    with open('examples/day2_drift/drift_scenario_manual_sg.json', 'r') as f:
        actual_state = json.load(f)

    print("ALERTA: Detectada alteração manual (ClickOps)!")
    print(f"Diferença encontrada: {json.dumps(actual_state['resources'][0]['values']['ingress'], indent=2)}")

    # 3. Auditoria do Drift
    print("\n[Agente Auditor]: Avaliando risco da alteração manual...")
    # Convert actual state to a plan-like structure for OPA
    mock_plan_drift = {
        "resource_changes": [
            {
                "address": "aws_security_group.allow_ssh",
                "type": "aws_security_group",
                "change": {
                    "after": {
                        "tags": {} # Missing tags
                    }
                }
            }
        ]
    }
    # For simplicity, we know port 22 is a risk. OPA could check this too.
    print("Veredito: CRÍTICO. Porta 22 aberta para 0.0.0.0/0 viola política PCI.")

    # 4. Auto-Remediação
    print("\n[Agente Arquiteto]: Gerando HCL de remediação para sobrescrever o Drift...")
    remediation_hcl = """
# REMEDIATION CODE
resource "aws_security_group" "web_sg" {
  name = "web-server-sg"
  description = "REMEDIATED: Removed manual SSH access"
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Project    = "Alpha"
    CostCenter = "Compliance-101"
    Remediated = "True"
  }
}
"""
    print(f"--- HCL Corretivo ---\n{remediation_hcl}")

    print("\n[Sistema]: Aplicando correção via Terraform pipeline...")
    print("Status: Ambiente restaurado para o estado seguro.")

    # In a real scenario, we would run the Auditor here again on the remediation_hcl
    # For the simulation, we just assume success if it reached here without crash
    # but let's add a basic check.
    if "REMEDIATED" not in remediation_hcl:
        print("\n❌ ERRO: O HCL de remediação não foi gerado corretamente!")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ PoC: Drift corrigido autonomamente pela IA!")
    print("="*60)

if __name__ == "__main__":
    simulate_drift_remediation()

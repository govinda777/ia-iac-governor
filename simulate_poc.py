import json
import os
import sys
from workflow.tools import NetworkInventoryTool, GovernanceManagerTool

def simulate_creation_flow():
    print("\n" + "="*60)
    print("🚀 SIMULAÇÃO: Ciclo de Criação de Infraestrutura Goverunada (Pluggable)")
    print("="*60)

    # 1. Intenção do Usuário
    intent = "Preciso de um bucket S3 para logs e um banco de dados RDS."
    print(f"\n[Usuário]: {intent}")

    # 2. Agente Arquiteto em ação (Mock)
    print("\n[Agente Arquiteto]: Gerando HCL inicial...")

    # Simulando um erro inicial do arquiteto (esqueceu criptografia no S3 e deixou RDS público)
    initial_hcl = """
resource "aws_s3_bucket" "logs" {
  bucket = "alpha-audit-logs"
}

resource "aws_db_instance" "alpha_db" {
  instance_class      = "db.t3.medium"
  identifier          = "alpha-db"
  publicly_accessible = true
}
"""
    print(f"--- HCL Gerado (Tentativa 1) ---\n{initial_hcl}")

    # 3. Agente Auditor em ação
    print("\n[Agente Auditor]: Iniciando Auditoria via GovernanceManager...")
    gov_tool = GovernanceManagerTool()

    audit_result = gov_tool._run(initial_hcl)
    print(f"\nResultado da Auditoria:\n{audit_result}")

    # 4. Agente Arquiteto Corrige usando os patches
    print("\n[Agente Arquiteto]: Corrigindo falhas apontadas e aplicando patches...")

    # Simulando a aplicação do patch sugerido pelo Firefly e correção do RDS
    final_hcl = """
resource "aws_s3_bucket" "logs" {
  bucket = "alpha-audit-logs"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_db_instance" "alpha_db" {
  instance_class      = "db.t3.medium"
  identifier          = "alpha-db"
  publicly_accessible = false
  storage_encrypted   = true
  tags = {
    Project    = "Alpha"
    CostCenter = "Research-01"
  }
}
"""
    print(f"--- HCL Final (Corrigido) ---\n{final_hcl}")

    # 5. Re-Auditoria
    print("\n[Agente Auditor]: Re-auditando...")
    final_audit = gov_tool._run(final_hcl)
    print(f"\nResultado da Auditoria Final:\n{final_audit}")

    if "VERDICT: APPROVED" not in final_audit:
        print("\n❌ ERRO: A auditoria final deveria ter sido aprovada!")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ PoC: Infraestrutura provisionada com conformidade total (Multi-Layer)!")
    print("="*60)

if __name__ == "__main__":
    simulate_creation_flow()

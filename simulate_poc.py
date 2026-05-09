import json

def simulate():
    print("\n--- Iniciando PoC de Governança AI-Native ---")
    print("Intenção do Usuário: 'Preciso de um bucket S3 para armazenar logs de auditoria do projeto Alpha.'\n")

    print("[Agente Arquiteto]: Gerando código HCL inicial...")
    initial_hcl = """
resource "aws_s3_bucket" "example" {
  bucket = "audit-logs-alpha"
  tags = {
    Name = "AuditLogsAlpha"
  }
}
"""
    print(f"--- Código Gerado ---\n{initial_hcl}")

    print("[Agente Sentinel]: Consultando Grafo de Segurança (schema/security_graph.json)...")
    with open('schema/security_graph.json', 'r') as f:
        graph = json.load(f)
    risks = graph.get('risks', [])
    print(f"Alerta: Encontrado risco '{risks[0]['name']}' no ambiente.")

    print("\n[Agente Auditor]: Executando 'opa exec' com políticas em 'policies/compliance.rego'...")
    print("Resultado OPA: DENIED")
    print("- Faltando tags: CostCenter, Project")
    print("- Faltando criptografia: storage_encrypted")

    print("\n[Agente Auditor]: Análise de Contexto de Segurança:")
    print("AVISO: O bucket 'audit-logs-alpha' será acessível por instâncias em subnets públicas.")
    print("RECOMENDAÇÃO: Forçar 'Public Access Block' e Criptografia SSE-KMS.")

    print("\n[Agente Arquiteto]: Refletindo sobre o feedback e corrigindo o código...")
    final_hcl = """
resource "aws_s3_bucket" "example" {
  bucket = "audit-logs-alpha"
  tags = {
    Name       = "AuditLogsAlpha"
    CostCenter = "Compliance-101"
    Project    = "Alpha"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
"""
    print(f"--- HCL Final Goverunado ---\n{final_hcl}")
    print("\n--- PoC Finalizada com Sucesso ---")

if __name__ == "__main__":
    simulate()

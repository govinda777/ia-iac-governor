# Remediação: The Shadow Admin (Cross-Account)

## Por que a análise de grafos é superior?

Neste cenário, se analisarmos o `tfstate` ou o código HCL da **Conta A** isoladamente, veremos apenas uma Role com permissão para assumir outra Role em outra conta. Não sabemos se essa Role de destino é perigosa ou se a confiança está configurada corretamente.

Se analisarmos apenas a **Conta B**, veremos uma Role de Administrador que confia na Conta A. Pode parecer legítimo para fins administrativos.

**A superioridade do Grafo:**
O motor de grafos correlaciona os dois nós (Conta A e Conta B) através da aresta `sts:AssumeRole`. Ele permite identificar que um principal de uma conta menos privilegiada (ou sandbox) tem um caminho direto para o `AdministratorAccess` em uma conta de produção, sem as proteções necessárias como `Condition: {"Bool": {"aws:MultiFactorAuthPresent": "true"}}`.

## Medidas de Remediação

1.  **Impor MFA:** Adicionar uma condição de MFA na Trust Policy da Role na Conta B.
2.  **Restrição de IP:** Limitar o acesso a IPs corporativos conhecidos.
3.  **Princípio do Menor Privilégio:** Em vez de `AdministratorAccess`, conceder apenas as permissões granulares necessárias para a tarefa Cross-Account.
4.  **Uso de External ID:** Exigir um `sts:ExternalId` para evitar o problema do "Confused Deputy" em relações de confiança entre terceiros ou contas distintas.

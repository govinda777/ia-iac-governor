# Remediação: The Shared Artifact Poisoning

## Por que a análise de grafos é superior?

Muitas ferramentas de análise estática de HCL focam apenas em `Principal: "*"` sem condições. Ao ver a condição `aws:PrincipalOrgID`, a ferramenta pode considerar o risco como "Médio" ou até "Baixo", pois teoricamente apenas usuários da empresa podem acessar.

**A superioridade do Grafo:**
O Grafo consegue identificar que o "raio de explosão" de um bucket de artefatos de produção se estende a todas as contas da organização. Ele mapeia que o nó `S3Bucket` é um "Source" para um nó `CodePipeline` ou `CodeBuild`. Ao correlacionar a criticidade do bucket (artefatos de execução) com a permissividade da política (toda a Org), o Grafo eleva a severidade para Crítica, alertando que um desenvolvedor de uma conta de testes pode injetar código no binário que roda na produção.

## Medidas de Remediação

1.  **Isolamento de Escrita:** Nunca usar `aws:PrincipalOrgID` para permissões de escrita (`PutObject`). As permissões de escrita devem ser restritas a ARNs de Roles específicas da conta de CI/CD.
2.  **Uso de Read-Only para a Org:** O uso do OrgID é aceitável para leitura de artefatos públicos internos, mas nunca para modificação.
3.  **Habilitar Versionamento e MFA Delete:** Garantir que versões anteriores do objeto não sejam perdidas e que a deleção exija MFA.
4.  **Assinatura de Artefatos:** Implementar assinatura digital (ex: AWS Signer) para garantir que o pipeline só execute artefatos cuja integridade e origem foram verificadas.

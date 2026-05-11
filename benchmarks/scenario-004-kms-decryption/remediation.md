# Remediação: Cross-Account KMS Decryption

## Por que a análise de grafos é superior?

Analisar uma Key Policy isoladamente pode levar a falsos negativos. Permitir que outra conta da mesma organização acesse uma chave pode parecer uma configuração de compartilhamento legítima. No entanto, sem saber *quem* na conta de destino está usando a chave e para *qual* finalidade, o risco permanece oculto.

**A superioridade do Grafo:**
O Grafo identifica que a relação de confiança é feita com o `root` da conta de desenvolvimento. Isso significa que *qualquer* entidade na conta de desenvolvimento com permissões KMS pode decifrar dados da produção. O Grafo mapeia a aresta de decriptografia entre as duas contas e sinaliza que segredos de produção estão acessíveis por um ambiente de menor confiança (Dev), violando o isolamento de dados.

## Medidas de Remediação

1.  **Restrição de Principais:** Nunca conceder permissão ao `root` de outra conta. Especifique ARNs de Roles ou Usuários exatos que precisam de acesso.
2.  **Uso de Encryption Context:** Forçar o uso de um `encryption context` nas operações de decriptografia para garantir que a chave só seja usada no contexto esperado (ex: por uma aplicação específica).
3.  **Monitoramento com CloudTrail:** Auditar rigorosamente quem de fora da conta está utilizando as chaves KMS da produção.
4.  **KMS Grant com Restrições:** Utilizar `KMS Grants` em vez de políticas de chave permanentes para acessos temporários ou específicos de serviços, permitindo maior controle e revogação.

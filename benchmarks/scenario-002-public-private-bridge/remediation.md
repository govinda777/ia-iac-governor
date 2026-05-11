# Remediação: The Public-Private Bridge

## Por que a análise de grafos é superior?

Se analisarmos os arquivos de estado individualmente:
- Na **Sandbox**, vemos um peering para outra conta. É comum em arquiteturas multicloud ou multi-account.
- Na **Produção**, vemos um Security Group liberando a porta 3306 para um CIDR `10.1.0.0/16`. Sem o contexto de que este CIDR pertence a uma conta de "Sandbox" e está conectado via Peering, isso pode passar por uma configuração de rede interna normal.

**A superioridade do Grafo:**
O Grafo conecta a topologia de rede através de múltiplas contas. Ele identifica que um recurso na `Subnet Pública` (com Internet Gateway) da Conta Sandbox tem um caminho de rede roteável até o nó `RDS` na Conta de Produção. O Grafo sinaliza o risco de "Transitional Network Exposure", onde a sandbox vira um bastion não oficial para a produção.

## Medidas de Remediação

1.  **Segregação de Ambientes:** Evitar Peering direto entre Sandbox e Produção. Usar um Transit Gateway com políticas de inspeção (Firewall).
2.  **Zero Trust Networking:** Em vez de liberar CIDRs inteiros nos Security Groups, utilizar referências de IDs de Security Group (se estiverem na mesma região/via TGW) ou identidades de aplicação (Service Mesh).
3.  **Privilégio de Rede:** Garantir que apenas sub-redes privadas específicas tenham rotas para a rede de produção, e nunca sub-redes públicas.
4.  **Network Access Control Lists (NACLs):** Implementar regras explícitas de negação entre CIDRs de ambientes diferentes como segunda camada de defesa.

# Provedores de Governança (Providers)

Este diretório contém as implementações concretas do `GovernanceProvider`. Cada classe encapsula uma heurística, integração de IA, ou mecanismo determinístico de checagem contra o código Terraform avaliado.

### Provedores Ativos:

1. **`CostProvider`**:
   - Realiza verificação de custo estimada cruzando tipos e instâncias contidos nas mudanças.
2. **`OPAProvider`**:
   - Executa a política principal Open Policy Agent sobre o JSON do plano. Checa tags e restrições rígidas.
3. **`FireflyProvider`**:
   - Fornece um mecanismo integrado (simulado ou integrado com API) para auditar componentes nativos ou com suporte LLM.
4. **`GraphProvider`**:
   - O mais avançado dos provedores locais. Consome o plano (`resource_changes`) de forma estruturada para construir heurísticas em cima do `schema/security_graph.json` detectando Combinações Tóxicas complexas (Ex: Um acesso S3 irrestrito + um mapa com IP Público).

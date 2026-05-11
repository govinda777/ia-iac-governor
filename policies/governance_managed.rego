package governance_managed

import future.keywords.if

# Negar se houver uma rota para Internet Gateway (IGW) ligada a uma subnet marcada como ComplianceTier: private
deny[msg] {
    # 1. Encontrar associações de tabela de rotas ou rotas diretas
    resource := input.resource_changes[_]
    resource.type == "aws_route"

    # 2. Verificar se o destino é um Internet Gateway
    resource.change.after.gateway_id != null
    startswith(resource.change.after.gateway_id, "igw-")

    # 3. Identificar a subnet associada (via route_table ou direct association)
    # Aqui simulamos a busca pela subnet no plano que tenha a tag de conformidade
    subnet := input.resource_changes[_]
    subnet.type == "governor_managed_subnet"
    subnet.change.after.tier == "private"

    # 4. Validar se a rota se aplica a esta subnet privada
    # (Em um grafo real, verificaríamos a associação da RT. Aqui simplificamos para a regra de negócio)
    msg := sprintf("Segurança: Bloqueio de rota pública para subnet privada do projeto '%s'. Subnets com tier 'private' não podem ter rotas para Internet Gateway.", [subnet.change.after.project_name])
}

# Regra alternativa: Validar tags de conformidade diretamente no recurso gerenciado
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "governor_managed_subnet"

    # Garantir que o tier seja válido
    not valid_tier(resource.change.after.tier)
    msg := sprintf("Governança: O tier '%s' é inválido para o recurso governor_managed_subnet.", [resource.change.after.tier])
}

valid_tier(t) {
    t == "public"
}
valid_tier(t) {
    t == "private"
}

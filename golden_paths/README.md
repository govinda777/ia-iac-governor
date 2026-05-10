# 🛣️ Golden Paths (Caminhos de Ouro)

O conceito de **Golden Path** visa fornecer aos desenvolvedores modelos de infraestrutura pré-aprovados, seguros e prontos para produção.

## 🌟 O que são Golden Paths?

São módulos Terraform altamente opinativos que encapsulam as melhores práticas da organização. Ao utilizar um Golden Path, o desenvolvedor garante que a infraestrutura gerada já passou pelos requisitos básicos de segurança e conformidade.

## 🏗️ Arquitetura de uma Aplicação Padrão

O módulo `standard-application` define uma topologia resiliente e segura por padrão.

```mermaid
graph TD
    subgraph "Standard Application Module"
    ALB[Application Load Balancer] --> ASG[Auto Scaling Group]
    ASG --> EC2[Instâncias EC2]
    EC2 --> RDS[Banco de Dados RDS (Private)]
    EC2 --> S3[Bucket S3 (Encrypted)]
    end

    subgraph "Segurança Nativa"
    EC2 --- SG[Security Groups Restritos]
    RDS --- KMS[KMS Encryption]
    S3 --- Policy[Bucket Policy Strict]
    end
```

## 📦 Módulos Disponíveis

- **`standard-application/`**: Módulo para aplicações web padrão, incluindo balanceamento de carga, computação escalar e persistência de dados.

## ✅ Vantagens

1.  **Velocidade:** Reduz o tempo de setup de novos projetos.
2.  **Conformidade:** Menos chances de erro humano em configurações críticas.
3.  **Auditabilidade:** Facilita o trabalho do Agente Auditor, pois os módulos já são conhecidos e confiáveis.

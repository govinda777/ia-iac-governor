package governance

import (
	"context"
	"fmt"
)

// IPAMConfig representa a configuração retornada pela API de governança interna.
type IPAMConfig struct {
	CidrBlock        string
	VpcId            string
	AvailabilityZone string
	DefaultTags      map[string]string
}

// GetIPAMConfig simula uma chamada de API interna para obter configurações de rede baseadas no projeto e tier.
// Em uma implementação real, isso consultaria um serviço de IPAM ou um Banco de Dados de Governança.
func GetIPAMConfig(ctx context.Context, projectName string, tier string) (*IPAMConfig, error) {
	// Mock de lógica de negócio:
	// Projetos diferentes ou tiers diferentes recebem sub-redes e VPCs distintas.

	config := &IPAMConfig{
		DefaultTags: map[string]string{
			"Project":        projectName,
			"Tier":           tier,
			"ManagedBy":      "GovernorProvider",
			"ComplianceTier": tier,
		},
	}

	switch tier {
	case "public":
		config.CidrBlock = "10.0.1.0/24"
		config.VpcId = "vpc-0a1b2c3d4e5f6g7h8" // VPC Pública Homologada
		config.AvailabilityZone = "us-east-1a"
	case "private":
		config.CidrBlock = "10.0.2.0/24"
		config.VpcId = "vpc-9i8j7k6l5m4n3o2p1" // VPC Privada Homologada
		config.AvailabilityZone = "us-east-1b"
	default:
		return nil, fmt.Errorf("tier desconhecido: %s", tier)
	}

	return config, nil
}

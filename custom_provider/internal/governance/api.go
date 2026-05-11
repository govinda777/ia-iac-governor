package governance

import (
	"context"
	"fmt"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
	"github.com/aws/aws-sdk-go-v2/service/ec2/types"
)

// SubnetProvisionResponse representa o resultado do provisionamento feito pelo departamento de Redes.
type SubnetProvisionResponse struct {
	SubnetId         string
	VpcId            string
	CidrBlock        string
	AvailabilityZone string
	Arn              string
	Status           string
	Tags             map[string]string
}

// ProvisionSubnet centraliza a lógica de orquestração do departamento de Redes.
// Em um cenário real, isso poderia ser uma chamada gRPC ou REST para outro serviço,
// ou como neste caso, uma lógica encapsulada que utiliza o SDK da AWS para garantir
// que a infraestrutura atenda aos padrões da empresa.
func ProvisionSubnet(ctx context.Context, client *ec2.Client, projectName string, tier string) (*SubnetProvisionResponse, error) {
	// 1. Lógica do Departamento de Redes: Selecionar ou criar a VPC correta.
	// Aqui simulamos a decisão de arquitetura baseada no tier.
	vpcId := "vpc-0a1b2c3d4e5f6g7h8"
	cidr := "10.0.1.0/24"
	az := "us-east-1a"

	if tier == "private" {
		vpcId = "vpc-9i8j7k6l5m4n3o2p1"
		cidr = "10.0.2.0/24"
		az = "us-east-1b"
	}

	// 2. Orquestração Real via SDK (Executada em nome do Departamento de Redes)
	tags := []types.Tag{
		{Key: aws.String("Project"), Value: aws.String(projectName)},
		{Key: aws.String("Tier"), Value: aws.String(tier)},
		{Key: aws.String("ComplianceTier"), Value: aws.String(tier)},
		{Key: aws.String("ManagedBy"), Value: aws.String("NetworkDepartment")},
	}

	input := &ec2.CreateSubnetInput{
		VpcId:            aws.String(vpcId),
		CidrBlock:        aws.String(cidr),
		AvailabilityZone: aws.String(az),
		TagSpecifications: []types.TagSpecification{
			{
				ResourceType: types.ResourceTypeSubnet,
				Tags:         tags,
			},
		},
	}

	output, err := client.CreateSubnet(ctx, input)
	if err != nil {
		// Se a subnet já existir (idempotência), retornamos os dados dela
		if strings.Contains(err.Error(), "InvalidSubnet.Conflict") {
			return getExistingSubnet(ctx, client, vpcId, cidr)
		}
		return nil, fmt.Errorf("falha no provisionamento do departamento de redes: %w", err)
	}

	// 3. Mapeamento para o contrato da interface
	respTags := make(map[string]string)
	for _, t := range output.Subnet.Tags {
		respTags[*t.Key] = *t.Value
	}

	return &SubnetProvisionResponse{
		SubnetId:         *output.Subnet.SubnetId,
		VpcId:            *output.Subnet.VpcId,
		CidrBlock:        *output.Subnet.CidrBlock,
		AvailabilityZone: *output.Subnet.AvailabilityZone,
		Arn:              *output.Subnet.SubnetArn,
		Status:           string(output.Subnet.State),
		Tags:             respTags,
	}, nil
}

func getExistingSubnet(ctx context.Context, client *ec2.Client, vpcId, cidr string) (*SubnetProvisionResponse, error) {
	input := &ec2.DescribeSubnetsInput{
		Filters: []types.Filter{
			{Name: aws.String("vpc-id"), Values: []string{vpcId}},
			{Name: aws.String("cidr-block"), Values: []string{cidr}},
		},
	}
	output, err := client.DescribeSubnets(ctx, input)
	if err != nil || len(output.Subnets) == 0 {
		return nil, fmt.Errorf("conflito detectado mas não foi possível encontrar subnet existente")
	}

	s := output.Subnets[0]
	respTags := make(map[string]string)
	for _, t := range s.Tags {
		respTags[*t.Key] = *t.Value
	}

	return &SubnetProvisionResponse{
		SubnetId:         *s.SubnetId,
		VpcId:            *s.VpcId,
		CidrBlock:        *s.CidrBlock,
		AvailabilityZone: *s.AvailabilityZone,
		Arn:              *s.SubnetArn,
		Status:           string(s.State),
		Tags:             respTags,
	}, nil
}

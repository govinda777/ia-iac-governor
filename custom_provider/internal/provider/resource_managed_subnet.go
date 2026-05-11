package provider

import (
	"context"
	"fmt"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
	awstypes "github.com/aws/aws-sdk-go-v2/service/ec2/types"
	"github.com/hashicorp/terraform-plugin-framework/path"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
	"github.com/hashicorp/terraform-plugin-framework/types"
	"github.com/username/terraform-provider-governor/internal/governance"
)

// Certifique-se de que a implementação satisfaz a interface do framework.
var _ resource.Resource = &managedSubnetResource{}
var _ resource.ResourceWithImportState = &managedSubnetResource{}

func NewManagedSubnetResource() resource.Resource {
	return &managedSubnetResource{}
}

type managedSubnetResource struct {
	client *ec2.Client
}

type managedSubnetResourceModel struct {
	ID               types.String `tfsdk:"id"`
	ProjectName      types.String `tfsdk:"project_name"`
	Tier             types.String `tfsdk:"tier"`
	CidrBlock        types.String `tfsdk:"cidr_block"`
	VpcId            types.String `tfsdk:"vpc_id"`
	AvailabilityZone types.String `tfsdk:"availability_zone"`
	Arn              types.String `tfsdk:"arn"`
	Status           types.String `tfsdk:"status"`
}

func (r *managedSubnetResource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_managed_subnet"
}

func (r *managedSubnetResource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		MarkdownDescription: "Recurso de Subnet gerenciada que aplica regras de governança e soberania de infraestrutura.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "ID da Subnet na AWS.",
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.UseStateForUnknown(),
				},
			},
			"project_name": schema.StringAttribute{
				Required:            true,
				MarkdownDescription: "Nome do projeto associado à subnet.",
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.RequiresReplace(),
				},
			},
			"tier": schema.StringAttribute{
				Required:            true,
				MarkdownDescription: "Tier da subnet (ex: public, private).",
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.RequiresReplace(),
				},
			},
			"cidr_block": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "Bloco CIDR alocado automaticamente pelo IPAM de governança.",
			},
			"vpc_id": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "ID da VPC selecionada pela governança.",
			},
			"availability_zone": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "Zona de disponibilidade da subnet.",
			},
			"arn": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "ARN da Subnet na AWS.",
			},
			"status": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "Status atual da subnet.",
			},
		},
	}
}

func (r *managedSubnetResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}

	// Em um provedor real, o cliente AWS seria configurado no Configure do Provedor e passado aqui.
	// Para este exemplo, criamos um cliente padrão.
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		resp.Diagnostics.AddError("Erro ao carregar configuração AWS", err.Error())
		return
	}
	r.client = ec2.NewFromConfig(cfg)
}

func (r *managedSubnetResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan managedSubnetResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// 1. Enforcement de Governança
	govConfig, err := governance.GetIPAMConfig(ctx, plan.ProjectName.ValueString(), plan.Tier.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Erro de Governança", fmt.Sprintf("Não foi possível obter configuração de IPAM: %s", err))
		return
	}

	// 2. Orquestração AWS (SDK v2)
	// Nota: Em ambiente sandbox sem credenciais reais, isso falhará.
	// O requisito pede código real com tratamento de erro.

	tags := []awstypes.Tag{}
	for k, v := range govConfig.DefaultTags {
		tags = append(tags, awstypes.Tag{
			Key:   aws.String(k),
			Value: aws.String(v),
		})
	}

	input := &ec2.CreateSubnetInput{
		VpcId:            aws.String(govConfig.VpcId),
		CidrBlock:        aws.String(govConfig.CidrBlock),
		AvailabilityZone: aws.String(govConfig.AvailabilityZone),
		TagSpecifications: []awstypes.TagSpecification{
			{
				ResourceType: awstypes.ResourceTypeSubnet,
				Tags:         tags,
			},
		},
	}

	output, err := r.client.CreateSubnet(ctx, input)
	if err != nil {
		resp.Diagnostics.AddError("Erro ao criar Subnet na AWS", err.Error())
		return
	}

	// 3. Mapeamento de Estado
	plan.ID = types.StringValue(*output.Subnet.SubnetId)
	plan.CidrBlock = types.StringValue(*output.Subnet.CidrBlock)
	plan.VpcId = types.StringValue(*output.Subnet.VpcId)
	plan.AvailabilityZone = types.StringValue(*output.Subnet.AvailabilityZone)
	plan.Arn = types.StringValue(*output.Subnet.SubnetArn)
	plan.Status = types.StringValue(string(output.Subnet.State))

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

func (r *managedSubnetResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var state managedSubnetResourceModel
	diags := req.State.Get(ctx, &state)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	input := &ec2.DescribeSubnetsInput{
		SubnetIds: []string{state.ID.ValueString()},
	}

	output, err := r.client.DescribeSubnets(ctx, input)
	if err != nil {
		// Se a subnet não existir, limpa o estado para indicar drift (necessidade de recriação)
		if strings.Contains(err.Error(), "NotFound") {
			resp.State.RemoveResource(ctx)
			return
		}
		resp.Diagnostics.AddError("Erro ao ler Subnet na AWS", err.Error())
		return
	}

	if len(output.Subnets) == 0 {
		resp.State.RemoveResource(ctx)
		return
	}

	subnet := output.Subnets[0]
	state.CidrBlock = types.StringValue(*subnet.CidrBlock)
	state.VpcId = types.StringValue(*subnet.VpcId)
	state.AvailabilityZone = types.StringValue(*subnet.AvailabilityZone)
	state.Arn = types.StringValue(*subnet.SubnetArn)
	state.Status = types.StringValue(string(subnet.State))

	diags = resp.State.Set(ctx, &state)
	resp.Diagnostics.Append(diags...)
}

func (r *managedSubnetResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var plan managedSubnetResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Atualizações de metadados/tags
	govConfig, err := governance.GetIPAMConfig(ctx, plan.ProjectName.ValueString(), plan.Tier.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Erro de Governança no Update", err.Error())
		return
	}

	tags := []awstypes.Tag{}
	for k, v := range govConfig.DefaultTags {
		tags = append(tags, awstypes.Tag{
			Key:   aws.String(k),
			Value: aws.String(v),
		})
	}

	_, err = r.client.CreateTags(ctx, &ec2.CreateTagsInput{
		Resources: []string{plan.ID.ValueString()},
		Tags:      tags,
	})
	if err != nil {
		resp.Diagnostics.AddError("Erro ao atualizar Tags na AWS", err.Error())
		return
	}

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

func (r *managedSubnetResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var state managedSubnetResourceModel
	diags := req.State.Get(ctx, &state)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	_, err := r.client.DeleteSubnet(ctx, &ec2.DeleteSubnetInput{
		SubnetId: aws.String(state.ID.ValueString()),
	})
	if err != nil {
		if !strings.Contains(err.Error(), "NotFound") {
			resp.Diagnostics.AddError("Erro ao deletar Subnet na AWS", err.Error())
			return
		}
	}
}

func (r *managedSubnetResource) ImportState(ctx context.Context, req resource.ImportStateRequest, resp *resource.ImportStateResponse) {
	resource.ImportStatePassthroughID(ctx, path.Root("id"), req, resp)
}

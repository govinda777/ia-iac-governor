package provider

import (
	"context"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
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
		MarkdownDescription: "Recurso de Subnet gerenciada que delega o provisionamento ao departamento de Redes.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "ID da Subnet gerado pelo departamento de Redes.",
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.UseStateForUnknown(),
				},
			},
			"project_name": schema.StringAttribute{
				Required:            true,
				MarkdownDescription: "Nome do projeto para o qual o departamento de Redes alocará recursos.",
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.RequiresReplace(),
				},
			},
			"tier": schema.StringAttribute{
				Required:            true,
				MarkdownDescription: "Tier da infraestrutura desejada.",
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.RequiresReplace(),
				},
			},
			"cidr_block": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "Bloco CIDR definido pelo departamento.",
			},
			"vpc_id": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "VPC selecionada ou criada pelo departamento.",
			},
			"availability_zone": schema.StringAttribute{
				Computed:            true,
				MarkdownDescription: "AZ definida pela governança de Redes.",
			},
			"arn": schema.StringAttribute{
				Computed:            true,
			},
			"status": schema.StringAttribute{
				Computed:            true,
			},
		},
	}
}

func (r *managedSubnetResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
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

	// 🧠 Lógica de Negócio / Orquestração:
	// O provedor não chama o ec2.CreateSubnet diretamente.
	// Ele chama a API do departamento responsável, que abstrai a complexidade.
	govResp, err := governance.ProvisionSubnet(ctx, r.client, plan.ProjectName.ValueString(), plan.Tier.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Erro de Orquestração (Redes)", err.Error())
		return
	}

	// 🛠 Mapeamento de Estado:
	// O provedor apenas persiste o que foi resolvido pelo departamento.
	plan.ID = types.StringValue(govResp.SubnetId)
	plan.CidrBlock = types.StringValue(govResp.CidrBlock)
	plan.VpcId = types.StringValue(govResp.VpcId)
	plan.AvailabilityZone = types.StringValue(govResp.AvailabilityZone)
	plan.Arn = types.StringValue(govResp.Arn)
	plan.Status = types.StringValue(govResp.Status)

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

	// O Read continua usando o SDK para garantir que o recurso persiste na AWS
	// e detectar drift externo (alguém deletou manualmente fora do Terraform).
	input := &ec2.DescribeSubnetsInput{
		SubnetIds: []string{state.ID.ValueString()},
	}

	output, err := r.client.DescribeSubnets(ctx, input)
	if err != nil {
		if strings.Contains(err.Error(), "NotFound") {
			resp.State.RemoveResource(ctx)
			return
		}
		resp.Diagnostics.AddError("Erro ao ler recurso na AWS", err.Error())
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
	// Delegar ao departamento para aplicar atualizações se necessário
	var plan managedSubnetResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	_, err := governance.ProvisionSubnet(ctx, r.client, plan.ProjectName.ValueString(), plan.Tier.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Erro ao atualizar recurso via Orquestração", err.Error())
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
			resp.Diagnostics.AddError("Erro ao deletar recurso", err.Error())
			return
		}
	}
}

func (r *managedSubnetResource) ImportState(ctx context.Context, req resource.ImportStateRequest, resp *resource.ImportStateResponse) {
	resource.ImportStatePassthroughID(ctx, path.Root("id"), req, resp)
}

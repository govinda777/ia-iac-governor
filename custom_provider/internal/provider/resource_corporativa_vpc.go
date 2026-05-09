package provider

import (
	"context"

	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

func NewVPCResource() resource.Resource {
	return &vpcResource{}
}

type vpcResource struct{}

type vpcResourceModel struct {
	ID        types.String `tfsdk:"id"`
	Finalidade types.String `tfsdk:"finalidade"`
	CIDR      types.String `tfsdk:"cidr"`
}

func (r *vpcResource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_vpc"
}

func (r *vpcResource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true,
			},
			"finalidade": schema.StringAttribute{
				Required: true,
			},
			"cidr": schema.StringAttribute{
				Computed: true,
			},
		},
	}
}

func (r *vpcResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan vpcResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Simular POST para https://api.redes.corp/v1/provision
	// Mock: IPAM retorna CIDR baseado na finalidade
	if plan.Finalidade.ValueString() == "pci-compliant" {
		plan.CIDR = types.StringValue("10.0.1.0/24")
	} else {
		plan.CIDR = types.StringValue("172.16.0.0/16")
	}
	plan.ID = types.StringValue("vpc-custom-123")

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

func (r *vpcResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
}

func (r *vpcResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
}

func (r *vpcResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
}

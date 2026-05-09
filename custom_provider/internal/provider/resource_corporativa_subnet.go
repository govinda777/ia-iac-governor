package provider

import (
	"context"

	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

func NewSubnetResource() resource.Resource {
	return &subnetResource{}
}

type subnetResource struct{}

type subnetResourceModel struct {
	ID        types.String `tfsdk:"id"`
	VPCID     types.String `tfsdk:"vpc_id"`
	Finalidade types.String `tfsdk:"finalidade"`
	CIDR      types.String `tfsdk:"cidr"`
}

func (r *subnetResource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_subnet"
}

func (r *subnetResource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true,
			},
			"vpc_id": schema.StringAttribute{
				Required: true,
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

func (r *subnetResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan subnetResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Mock: IPAM retorna CIDR baseado na finalidade
	if plan.Finalidade.ValueString() == "pci-compliant" {
		plan.CIDR = types.StringValue("10.0.1.128/25")
	} else {
		plan.CIDR = types.StringValue("172.16.1.0/24")
	}
	plan.ID = types.StringValue("subnet-custom-456")

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

func (r *subnetResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {}
func (r *subnetResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {}
func (r *subnetResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {}

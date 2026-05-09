package provider

import (
	"context"

	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
	"github.com/hashicorp/terraform-plugin-framework/types"
	"github.com/hashicorp/terraform-plugin-log/tflog"
)

func NewSecurityGroupResource() resource.Resource {
	return &securityGroupResource{}
}

type securityGroupResource struct{}

type securityGroupResourceModel struct {
	ID       types.String `tfsdk:"id"`
	AppName  types.String `tfsdk:"app_name"`
	TicketID types.String `tfsdk:"ticket_id"`
	Status   types.String `tfsdk:"status"`
}

func (r *securityGroupResource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_security_group"
}

func (r *securityGroupResource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true,
			},
			"app_name": schema.StringAttribute{
				Required: true,
			},
			"ticket_id": schema.StringAttribute{
				Computed: true,
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.UseStateForUnknown(),
				},
			},
			"status": schema.StringAttribute{
				Computed: true,
			},
		},
	}
}

func (r *securityGroupResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan securityGroupResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Simular abertura de ticket via API
	ticketID := "TKT-998877"

	// Simular verificação de status
	status := "PENDENTE" // Mock: inicia pendente

	if status != "APROVADO" {
		resp.Diagnostics.AddError(
			"Aprovação Pendente",
			"O ticket de Security Group "+ticketID+" ainda não foi aprovado pelo time de Segurança.",
		)
		return
	}

	plan.ID = types.StringValue("sg-12345")
	plan.TicketID = types.StringValue(ticketID)
	plan.Status = types.StringValue(status)

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

func (r *securityGroupResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
}

func (r *securityGroupResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
}

func (r *securityGroupResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
}

func (r *securityGroupResource) ModifyPlan(ctx context.Context, req resource.ModifyPlanRequest, resp *resource.ModifyPlanResponse) {
	if req.Plan.Raw.IsNull() {
		return // Delete
	}

	// Se for um novo recurso, avisamos sobre o ticket
	if req.State.Raw.IsNull() {
		tflog.Warn(ctx, "Um novo ticket de aprovação será aberto para este Security Group.")
	}
}

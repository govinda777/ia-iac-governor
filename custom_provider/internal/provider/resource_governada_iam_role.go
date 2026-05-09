package provider

import (
	"context"

	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

func NewIAMRoleResource() resource.Resource {
	return &iamRoleResource{}
}

type iamRoleResource struct{}

type iamRoleResourceModel struct {
	ID                  types.String `tfsdk:"id"`
	Name                types.String `tfsdk:"name"`
	AssumeRolePolicy    types.String `tfsdk:"assume_role_policy"`
	PermissionsBoundary types.String `tfsdk:"permissions_boundary"`
}

func (r *iamRoleResource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_iam_role"
}

func (r *iamRoleResource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true,
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.UseStateForUnknown(),
				},
			},
			"name": schema.StringAttribute{
				Required: true,
			},
			"assume_role_policy": schema.StringAttribute{
				Required: true,
			},
			"permissions_boundary": schema.StringAttribute{
				Computed: true,
				Optional: true,
				PlanModifiers: []planmodifier.String{
					&iamSecurityModifier{},
				},
			},
		},
	}
}

type iamSecurityModifier struct{}

func (m *iamSecurityModifier) Description(_ context.Context) string {
	return "Injeta automaticamente a Permissions Boundary e condições de MFA via API de Segurança."
}

func (m *iamSecurityModifier) MarkdownDescription(_ context.Context) string {
	return "Injeta automaticamente a Permissions Boundary e condições de MFA via API de Segurança."
}

func (m *iamSecurityModifier) PlanModifyString(ctx context.Context, req planmodifier.StringRequest, resp *planmodifier.StringResponse) {
	// Mock da resposta da API de segurança
	mandatoryBoundary := "arn:aws:iam::123456789012:policy/CorporatePermissionsBoundary"

	// Injeta o valor forçadamente no plano
	resp.PlanValue = types.StringValue(mandatoryBoundary)
}

func (r *iamRoleResource) ModifyPlan(ctx context.Context, req resource.ModifyPlanRequest, resp *resource.ModifyPlanResponse) {
	if req.Plan.Raw.IsNull() {
		return
	}

	var plan iamRoleResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Mock de lógica: se a role tiver "admin" no nome, injetar condição MFA
	if !plan.Name.IsUnknown() && (plan.Name.ValueString() == "admin" || plan.Name.ValueString() == "critical") {
		mfaPolicy := `{
			"Version": "2012-10-17",
			"Statement": [{
				"Effect": "Allow",
				"Principal": {"Service": "ec2.amazonaws.com"},
				"Action": "sts:AssumeRole",
				"Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}
			}]
		}`
		plan.AssumeRolePolicy = types.StringValue(mfaPolicy)

		diags = resp.Plan.Set(ctx, &plan)
		resp.Diagnostics.Append(diags...)
	}
}

func (r *iamRoleResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var plan iamRoleResourceModel
	diags := req.Plan.Get(ctx, &plan)
	resp.Diagnostics.Append(diags...)
	if resp.Diagnostics.HasError() {
		return
	}

	// Simular criação chamando API
	plan.ID = types.StringValue("role-" + plan.Name.ValueString())

	diags = resp.State.Set(ctx, plan)
	resp.Diagnostics.Append(diags...)
}

func (r *iamRoleResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
}

func (r *iamRoleResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
}

func (r *iamRoleResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
}

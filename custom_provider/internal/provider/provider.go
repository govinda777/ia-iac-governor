package provider

import (
	"context"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/provider"
	"github.com/hashicorp/terraform-plugin-framework/resource"
)

func New() provider.Provider {
	return &governorProvider{}
}

type governorProvider struct{}

func (p *governorProvider) Metadata(_ context.Context, _ provider.MetadataRequest, resp *provider.MetadataResponse) {
	resp.TypeName = "governor"
}

func (p *governorProvider) Schema(_ context.Context, _ provider.SchemaRequest, resp *provider.SchemaResponse) {
}

func (p *governorProvider) Configure(_ context.Context, _ provider.ConfigureRequest, _ *provider.ConfigureResponse) {
}

func (p *governorProvider) DataSources(_ context.Context) []func() datasource.DataSource {
	return nil
}

func (p *governorProvider) Resources(_ context.Context) []func() resource.Resource {
	return []func() resource.Resource{
		NewIAMRoleResource,
		NewVPCResource,
		NewSubnetResource,
		NewSecurityGroupResource,
	}
}

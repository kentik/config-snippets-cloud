data "azuread_client_config" "current" {}

data "azuread_service_principals" "existing_vnet_flow_exporter" {
  client_ids     = [var.flow_exporter_application_id]
  ignore_missing = true
}

locals {
  vnet_flow_exporter_already_exists = length(data.azuread_service_principals.existing_vnet_flow_exporter.object_ids) == 1
}

# Creates Service Principal for pre-existing "Kentik VNet Flow Exporter" app, so the app can access flow logs in Azure cloud
# This resource is shared across Azure Account, so only create it if doesn't exist yet
resource "azuread_service_principal" "new_vnet_flow_exporter" {
  count = local.vnet_flow_exporter_already_exists ? 0 : 1

  client_id                    = var.flow_exporter_application_id
  app_role_assignment_required = false
  owners                       = [data.azuread_client_config.current.object_id]

  feature_tags {
    enterprise = true # show the app in AzurePortal under Enterprise Applications
  }
}

locals {
  kentik_vnet_flow_exporter_id = local.vnet_flow_exporter_already_exists ? data.azuread_service_principals.existing_vnet_flow_exporter.object_ids[0] : azuread_service_principal.new_vnet_flow_exporter[0].object_id
}

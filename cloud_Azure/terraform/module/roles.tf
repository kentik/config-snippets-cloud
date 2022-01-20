# Provide service principal Contributor role to storage account
resource "azurerm_role_assignment" "kentik_role_contributor" {
  scope                = azurerm_storage_account.kentik_storage_account.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.kentik_nsg_flow_exporter.object_id
}

# Provide service principal Reader role to Resource Group
resource "azurerm_role_assignment" "kentik_role_reader" {
  scope                = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}"
  role_definition_name = "Reader"
  principal_id         = azuread_service_principal.kentik_nsg_flow_exporter.object_id
}

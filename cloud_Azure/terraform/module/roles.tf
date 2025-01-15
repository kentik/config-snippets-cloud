# Provide service principal Contributor role to each storage account
resource "azurerm_role_assignment" "kentik_role_contributor" {
  for_each = azurerm_storage_account.logs_storage_account

  scope                = each.value.id
  role_definition_name = "Contributor"
  principal_id         = local.kentik_vnet_flow_exporter_id
}

# Provide service principal Reader role to each Resource Group
resource "azurerm_role_assignment" "kentik_role_reader" {
  for_each = toset(var.resource_group_names)

  scope                = "/subscriptions/${var.subscription_id}/resourceGroups/${each.value}"
  role_definition_name = "Reader"
  principal_id         = local.kentik_vnet_flow_exporter_id
}

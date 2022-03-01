# Provide service principal Contributor role to each storage account
resource "azurerm_role_assignment" "kentic_role_contributor" {
  count = length(azurerm_storage_account.logs_storage_account)

  scope                = azurerm_storage_account.logs_storage_account[count.index].id
  role_definition_name = "Contributor"
  principal_id         = local.kentik_nsg_flow_exporter_id
}

# Provide service principal Reader role to each Resource Group
resource "azurerm_role_assignment" "kentic_role_reader" {
  count = length(var.resource_group_names)

  scope                = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_names[count.index]}"
  role_definition_name = "Reader"
  principal_id         = local.kentik_nsg_flow_exporter_id
}

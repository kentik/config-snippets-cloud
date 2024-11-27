# Provide service principal Contributor role to each storage account
resource "azurerm_role_assignment" "kentik_role_contributor" {
  for_each = { for s, rg in var.resource_group_names : rg => s }

  scope                = azurerm_storage_account.logs_storage_account[each.value].id
  role_definition_name = "Contributor"
  principal_id         = local.kentik_nsg_flow_exporter_id
}

# Provide service principal Reader role to each Resource Group
resource "azurerm_role_assignment" "kentik_role_reader" {
  count = length(var.resource_group_names)

  scope                = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_names[count.index]}"
  role_definition_name = "Reader"
  principal_id         = local.kentik_nsg_flow_exporter_id
}

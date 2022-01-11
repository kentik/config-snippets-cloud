output network_security_groups {
  value = split(",", data.external.nsg_data_source.result.nsg)
  description = "List of network security groups"
}

output subscription_id {
  value = var.subscription_id
  description = "Subscription Id"
}

output resource_group {
  value       = var.resource_group_name
  description = "Resource group name"
}

output storage_account {
  value       = azurerm_storage_account.kentik_storage_account.name
  description = "Storage account name"
}

output principal_id {
  value = azuread_service_principal.kentik_nsg_flow_exporter.object_id
  description = "Principal ID for Kentik NSG Flow Exporter"
}
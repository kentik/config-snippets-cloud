output network_security_groups {
  value = [for v in local.flat_nsgs: v.nsg]
  description = "List of network security group IDs"
}

output subscription_id {
  value = var.subscription_id
  description = "Azure subscription ID"
}

output resource_group_names {
  value       = var.resource_group_names
  description = "Resource group names for which flow logs are being collected"
}

output storage_accounts {
  value       = azurerm_storage_account.logs_storage_account[*].name
  description = "Flow log storage account names"
}

output principal_id {
  value = azuread_service_principal.kentik_nsg_flow_exporter.object_id
  description = "Principal ID for Kentik NSG Flow Exporter"
}
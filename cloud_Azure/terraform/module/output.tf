output "vnet_ids" {
  value       = [for vnet in local.flat_vnets : vnet.value.id]
  description = "Id's of the Virtual Networks from which to collect flow logs"
}

output "subscription_id" {
  value       = var.subscription_id
  description = "Azure subscription ID"
}

output "resource_group_names" {
  value       = var.resource_group_names
  description = "Names of Resource Groups from which to collect flow logs"
}

output "storage_accounts" {
  value       = [for sa in azurerm_storage_account.logs_storage_account : sa.name]
  description = "Storage Account names where flow logs will be collected"
}

output "principal_id" {
  value       = local.kentik_nsg_flow_exporter_id
  description = "Service Principal ID created for Kentik NSG Flow Exporter application"
}

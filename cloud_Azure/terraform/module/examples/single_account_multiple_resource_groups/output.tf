
output "network_security_groups" {
  value       = module.kentik_azure_integration.network_security_groups
  description = "Id's of the Network Security Groups which flow logs will be collected"
}

output "subscription_id" {
  value       = module.kentik_azure_integration.subscription_id
  description = "Azure subscription ID"
}

output "resource_group_names" {
  value       = module.kentik_azure_integration.resource_group_names
  description = "Names of Resource Groups from which to collect flow logs"
}

output "storage_accounts" {
  value       = module.kentik_azure_integration.storage_accounts
  description = "Storage Account names where flow logs will be collected"
}

output "principal_id" {
  value       = module.kentik_azure_integration.principal_id
  description = "Service Principal ID created for Kentik NSG Flow Exporter application"
}
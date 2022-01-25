
output "network_security_groups" {
  value = module.kentik_azure_integration.network_security_groups
}

output "subscription_id" {
  value = module.kentik_azure_integration.subscription_id
}

output "resource_group_names" {
  value = module.kentik_azure_integration.resource_group_names
}

output "storage_accounts" {
  value = module.kentik_azure_integration.storage_accounts
}

output "principal_id" {
  value = module.kentik_azure_integration.principal_id
}
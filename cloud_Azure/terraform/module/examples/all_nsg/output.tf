
output "network_security_groups" {
  value = module.kentik_azure_integration.network_security_groups
}

output "subscription_id" {
  value = module.kentik_azure_integration.subscription_id
}

output "resource_group" {
  value = module.kentik_azure_integration.resource_group
}

output "storage_account" {
  value = module.kentik_azure_integration.storage_account
}

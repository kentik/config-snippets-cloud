output "account1_sub1" {
  description = "Kentik integration details for Account 1, Subscription 1"
  value = {
    subscription_id      = module.kentik_account1_sub1.subscription_id
    resource_group_names = module.kentik_account1_sub1.resource_group_names
    storage_accounts     = module.kentik_account1_sub1.storage_accounts
    vnet_ids             = module.kentik_account1_sub1.vnet_ids
    principal_id         = module.kentik_account1_sub1.principal_id
  }
}

output "account1_sub2" {
  description = "Kentik integration details for Account 1, Subscription 2"
  value = {
    subscription_id      = module.kentik_account1_sub2.subscription_id
    resource_group_names = module.kentik_account1_sub2.resource_group_names
    storage_accounts     = module.kentik_account1_sub2.storage_accounts
    vnet_ids             = module.kentik_account1_sub2.vnet_ids
    principal_id         = module.kentik_account1_sub2.principal_id
  }
}

output "account2_sub1" {
  description = "Kentik integration details for Account 2, Subscription 1"
  value = {
    subscription_id      = module.kentik_account2_sub1.subscription_id
    resource_group_names = module.kentik_account2_sub1.resource_group_names
    storage_accounts     = module.kentik_account2_sub1.storage_accounts
    vnet_ids             = module.kentik_account2_sub1.vnet_ids
    principal_id         = module.kentik_account2_sub1.principal_id
  }
}

output "account2_sub2" {
  description = "Kentik integration details for Account 2, Subscription 2"
  value = {
    subscription_id      = module.kentik_account2_sub2.subscription_id
    resource_group_names = module.kentik_account2_sub2.resource_group_names
    storage_accounts     = module.kentik_account2_sub2.storage_accounts
    vnet_ids             = module.kentik_account2_sub2.vnet_ids
    principal_id         = module.kentik_account2_sub2.principal_id
  }
}

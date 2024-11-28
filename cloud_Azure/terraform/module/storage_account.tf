# Prepare names that meet Azure Storage Account naming restrictions (only alphanum letters, max 24 length, Azure-wide unique)
# Each output name is concatenation of Resource Group name and Subscription ID, adjusted to naming restrictions
locals {
  _names                          = [for nsg in local.flat_nsgs : tostring("${nsg.value.name}${var.subscription_id}")]
  _lowercase_names                = [for name in local._names : lower(name)]
  _alphanum_lowercase_names       = [for name in local._lowercase_names : join("", regexall("[[:alnum:]]+", name))]
  generated_storage_account_names = [for name in local._alphanum_lowercase_names : substr(name, 0, 24)]
  # Generate a map of NSG keys to storage account names
  nsg_to_storage_account_name = {
    for nsg in local.flat_nsgs : nsg.key => local.generated_storage_account_names
  }
}


# Creates one storage account per nsg per resource group to store flow logs
# StorageAccounts are mapped 1:1+:1 to nsg(s) and resource_group_names
# Note that only one flow log can be associated with a storage account per region
resource "azurerm_storage_account" "logs_storage_account" {
  for_each = { for nsg in local.flat_nsgs : nsg.key => nsg.value }

  # Generate storage account per nsg(s) in each rg
  name                     = local.generated_storage_account_names[each.key]
  resource_group_name      = each.value.rg
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    app = var.resource_tag
  }
}

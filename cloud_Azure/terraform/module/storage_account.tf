# Prepare names that meet Azure Storage Account naming restrictions (only alphanum letters, max 24 length, Azure-wide unique)
# Each output name is concatenation of Resource Group name and Subscription ID, adjusted to naming restrictions
locals {
  _names                          = [for name in var.resource_group_names : "${name}${var.subscription_id}"]
  _lowercase_names                = [for name in local._names : lower(name)]
  _alphanum_lowercase_names       = [for name in local._lowercase_names : join("", regexall("[[:alnum:]]+", name))]
  generated_storage_account_names = [for name in local._alphanum_lowercase_names : substr(name, 0, 24)]
}

locals {
  # Create a map of resource group names to storage account names
  resource_group_to_storage_account = {
    for rg in var.resource_group_names : rg => (
      length(var.storage_account_names) == length(var.resource_group_names) ?
      var.storage_account_names[index(var.resource_group_names, rg)] :
      local.generated_storage_account_names[index(var.resource_group_names, rg)]
    )
  }
}

# Creates one storage account per resource group to store flow logs
# StorageAccounts are mapped 1:1 to resource_group_names and this fact is used to get storage account id for given resource group name
resource "azurerm_storage_account" "logs_storage_account" {
  for_each = local.resource_group_to_storage_account

  name                     = each.value
  resource_group_name      = each.key
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    app = var.resource_tag
  }
}

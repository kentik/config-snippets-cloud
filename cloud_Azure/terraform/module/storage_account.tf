# Prepare names that meet Azure Storage Account naming restrictions (only alphanum letters, max 24 length, Azure-wide unique)
# Each output name is concatenation of Resource Group name and Subscription ID, adjusted to naming restrictions
locals {
    _names = [for name in var.resource_group_names : "${name}${var.subscription_id}"]
    _lowercase_names = [for name in local._names: lower(name)]
    _alphanum_lowercase_names = [for name in local._lowercase_names: join("", regexall("[[:alnum:]]+", name))]
    generated_storage_account_names = [for name in local._alphanum_lowercase_names: substr(name, 0, 24)]
}

# Creates one storage account per resource group to store flow logs
# StorageAccounts are mapped 1:1 to resource_group_names and this fact is used to get storage account id for given resource group name 
resource "azurerm_storage_account" "logs_storage_account" {
  count = length(var.resource_group_names)
  
  # use either custom name if one is provided, or generated one
  name                     = length(var.storage_account_names) == length(var.resource_group_names) ? var.storage_account_names[count.index] : local.generated_storage_account_names[count.index]
  resource_group_name      = var.resource_group_names[count.index]
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    app = "kentik_flow_log_exporter"
  }
}
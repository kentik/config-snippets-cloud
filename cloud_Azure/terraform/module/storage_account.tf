# Prepare names that meet Azure Storage Account naming restrictions (only alphanum letters, max 24 length, Azure-wide unique)
# Each output name is concatenation of Resource Group name and Subscription ID, adjusted to naming restrictions
locals {
    sa_names = [for s in var.resource_group_names : "${s}${var.subscription_id}"]
    sa_lowercase_names = [for s in local.sa_names: lower(s)]
    sa_alphanum_lowercase_names = [for s in local.sa_lowercase_names: join("", regexall("[[:alnum:]]+", s))]
    sa_limitedlength_alphanum_lowercase_names = [for s in local.sa_alphanum_lowercase_names: substr(s, 0, 24)]
}

# Creates one storage account per resource group to store flow logs
# StorageAccounts are mapped 1:1 to resource_group_names and this fact is used to get storage account id for given resource group name 
resource "azurerm_storage_account" "logs_storage_account" {
  count = length(var.resource_group_names)
  
  name                     = local.sa_limitedlength_alphanum_lowercase_names[count.index]
  resource_group_name      = var.resource_group_names[count.index]
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    app = "kentik_flow_log_exporter"
  }
}
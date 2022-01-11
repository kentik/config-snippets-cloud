# Creates storage account to store flow logs
resource "azurerm_storage_account" "kentik_storage_account" {
  name                     = "${var.prefix}storage" # can only consist of lowercase letters and numbers, and must be between 3 and 24 characters long
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "staging"
  }
}

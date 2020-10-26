# Creates storage account to store flow logs
resource "azurerm_storage_account" "kentik_storage_account" {
  name                     = "${var.prefix}storage"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "staging"
  }
}

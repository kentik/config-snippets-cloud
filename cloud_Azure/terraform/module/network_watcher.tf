# Creates network watcher
resource "azurerm_network_watcher" "kentik_network_watcher" {
  name                = "${var.prefix}_network_watcher"
  location            = "${var.location}"
  resource_group_name = "${var.resource_group_name}"
}

# Runs python script to gather network security groups and expose it as a data source
data "external" "example" {
  program = ["python3", "${path.module}/get_nsg.py"]

  query = {
    network_security_groups = "nsg"
  }
}

# Turns on flow logs for all network securiti groups in resource group
resource "azurerm_network_watcher_flow_log" "kentik_network_flow_log" {
  for_each = toset(split(",", data.external.example.result.nsg))
  network_watcher_name = azurerm_network_watcher.kentik_network_watcher.name
  resource_group_name  = "${var.resource_group_name}"

  network_security_group_id = each.key
  storage_account_id        = azurerm_storage_account.kentik_storage_account.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 7
  }
}

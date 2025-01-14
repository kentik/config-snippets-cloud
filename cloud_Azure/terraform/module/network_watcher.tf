# Network Watcher is created automatically by Azure when VirtualNetwork is created or updated in the subscription
# see: https://docs.microsoft.com/en-us/azure/network-watcher/network-watcher-create
data "azurerm_network_watcher" "network_watcher" {
  name                = "NetworkWatcher_${var.location}" # Azure creates NetworkWatcher named exactly that
  resource_group_name = "NetworkWatcherRG"
}

# Fetch all VNets for each resource group
data "azurerm_resources" "vnet" {
  for_each            = toset(var.resource_group_names)
  type                = "Microsoft.Network/virtualNetworks"
  resource_group_name = each.key
}

# Map resource group names to their corresponding VNets
# Flatten map to list of objects
locals {
  flat_vnets = flatten([
    for rg in var.resource_group_names : [
      for vnet in data.azurerm_resources.vnet[rg].resources : {
        rg   = rg
        vnet = vnet.name
        id   = vnet.id
      }
    ] if length(data.azurerm_resources.vnet[rg].resources) > 0 # filter out resource groups without VNets
  ])
}

# Turns on vnet flow logs for all vnets in requested resource groups
resource "azurerm_network_watcher_flow_log" "kentik_network_flow_log" {
  for_each = { for vnet in local.flat_vnets : vnet.name => vnet }

  name                 = format("${var.name}-flowLogs-%s", each.key)
  network_watcher_name = data.azurerm_network_watcher.network_watcher.name
  resource_group_name  = each.value.rg

  target_resource_id = each.value.id
  storage_account_id = azurerm_storage_account.logs_storage_account[each.value.rg].id
  enabled            = true
  version            = 2
  retention_policy {
    enabled = true
    days    = 7
  }
  tags = {
    app = var.resource_tag
  }
}

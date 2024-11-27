# Network Watcher is created automatically by Azure when VirtualNetwork is created or updated in the subscription
# see: https://docs.microsoft.com/en-us/azure/network-watcher/network-watcher-create
data "azurerm_network_watcher" "network_watcher" {
  name                = "NetworkWatcher_${var.location}" # Azure creates NetworkWatcher named exactly that
  resource_group_name = "NetworkWatcherRG"
}

# Fetch all NSGs for each resource group
data "azurerm_resources" "nsg" {
  for_each            = toset(var.resource_group_names)
  type                = "Microsoft.Network/networkSecurityGroups"
  resource_group_name = each.key
}

# Convert nsg data output of map of lists of maps:
#{
#  "ResourceGroupName1" = [
#   {id = "NetworkSercurityGroupId1", resource_group_name = "ResourceGroupName1"},
#   {id = "NetworkSercurityGroupId2", resource_group_name = "ResourceGroupName1"},
#  ]
#  "ResourceGroupName2" = [
#   {id = "NetworkSercurityGroupId3", resource_group_name = "ResourceGroupName2"},
#   {id = "NetworkSercurityGroupId4", resource_group_name = "ResourceGroupName2"}
#  ]
#}
# to a list of objects:
#{
#  "ResourceGroupName1-NetworkSercurityGroupName1" = {
#   {id = "NetworkSercurityGroupId1", name = "NetworkSercurityGroupName1", rg = "ResourceGroupName1"}
#}
#  "ResourceGroupName1-NetworkSercurityGroupName2" = {
#   {id = "NetworkSercurityGroupId2", name = "NetworkSercurityGroupName2", rg = "ResourceGroupName1"}
#}
#  "ResourceGroupName2-NetworkSercurityGroupName3" = {
#   {id = "NetworkSercurityGroupId3", name = "NetworkSercurityGroupName3", rg = "ResourceGroupName2"}
#}
#  "ResourceGroupName2-NetworkSercurityGroupName4" = {
#   {id = "NetworkSercurityGroupId4", name = "NetworkSercurityGroupName4", rg = "ResourceGroupName2"}
#}
#}
locals {
  flat_nsgs = flatten([
    for rg, nsg_data in data.azurerm_resources.nsg : [
      for nsg in nsg_data.resources : {
        key = "${nsg.resource_group_name}-${nsg.name}"
        value = {
          rg   = nsg.resource_group_name
          name = nsg.name
          id   = nsg.id
        }
      }
    ]
  ])
}

# Turns on flow logs for all network security groups in requested resource groups
resource "azurerm_network_watcher_flow_log" "kentik_network_flow_log" {
  for_each = { for nsg in local.flat_nsgs : nsg.key => nsg.value }

  name                      = "${var.name}_flow_log_${each.value.name}"
  network_watcher_name      = data.azurerm_network_watcher.network_watcher.name
  resource_group_name       = "NetworkWatcherRG"
  network_security_group_id = each.value.id
  storage_account_id        = azurerm_storage_account.logs_storage_account[each.value.rg].id
  enabled                   = true
  version                   = 2
  retention_policy {
    enabled = true
    days    = 7
  }
  tags = {
    app = var.resource_tag
  }
}

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

# Convert map of lists of maps:
#{
#  "ResourceGroupName1" = [
#   {id = "NetworkSercurityGroupId1", rg = "ResourceGroupName1"},
#   {id = "NetworkSercurityGroupId2", rg = "ResourceGroupName1"},
#  ]
#  "RG2" = [
#   {id = "NetworkSercurityGroupId3", rg = "ResourceGroupName2"},
#   {id = "NetworkSercurityGroupId4", rg = "ResourceGroupName2"}
#  ]
#}
# to list of objects:
# [
#   {id = "NetworkSercurityGroupId1", rg = "ResourceGroupName1"},
#   {id = "NetworkSercurityGroupId2", rg = "ResourceGroupName1"},
#   {id = "NetworkSercurityGroupId3", rg = "ResourceGroupName2"},
#   {id = "NetworkSercurityGroupId4", rg = "ResourceGroupName2"}
# ]
locals {
  flat_nsgs = [
    for rg_name in var.resource_group_names : [
      for nsg in data.azurerm_resources.nsg[rg_name].resources : {
        id = nsg.id  # Network Security Group ID
        rg = rg_name # Resource Group Name
      }
    ] if length(data.azurerm_resources.nsg[rg_name].resources) > 0 # filter out Resource Groups that have no Network Security Groups
  ]
}

# Turns on flow logs for all network security groups in requested resource groups
resource "azurerm_network_watcher_flow_log" "kentik_network_flow_log" {
  for_each = local.flat_nsgs

  name                      = "${var.name}_flow_log_${index(keys(local.flat_nsgs), each.key) + 1}"
  network_watcher_name      = data.azurerm_network_watcher.network_watcher.name
  resource_group_name       = each.value.rg
  network_security_group_id = each.key
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

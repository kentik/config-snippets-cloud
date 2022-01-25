# Network Watcher is created automatically by Azure when VirtualNetwork is created or updated in the subscription, see:
# https://docs.microsoft.com/en-us/azure/network-watcher/network-watcher-create
data "azurerm_network_watcher" "network_watcher" {
  name                = "NetworkWatcher_${var.location}"
  resource_group_name = "NetworkWatcherRG"
}

# Runs python script to gather network security groups from each requested resource group
# Resulting "data.external.nsg_data_source.results" is a map of string -> string, eg.
# {
#   "ResourceGroupName1" -> "NetworkSercurityGroupId1,NetworkSecurityGroupId2",
#   "ResourceGroupName2" -> "NetworkSercurityGroupId3,NetworkSecurityGroupId4"
# }
data "external" "nsg_data_source" {
  program = ["python3", "${path.module}/get_nsg.py"]
  query = {
    resource_group_names = join(",", var.resource_group_names)
  }
}

# Convert map of string -> string:
# {
#   "ResourceGroupName1" -> "NetworkSercurityGroupId1,NetworkSecurityGroupId2",
#   "ResourceGroupName2" -> "NetworkSercurityGroupId3,NetworkSecurityGroupId4"
# }
# to list of objects:
# [
#   {rg = "ResourceGroupName1", nsg = "NetworkSercurityGroupId1"},
#   {rg = "ResourceGroupName1", nsg = "NetworkSercurityGroupId2"},
#   {rg = "ResourceGroupName2", nsg = "NetworkSercurityGroupId3"},
#   {rg = "ResourceGroupName2", nsg = "NetworkSercurityGroupId4"}
# ]
locals {
  flat_nsgs = flatten([ 
    for rg, nsg_list in data.external.nsg_data_source.result : [
      for nsg in split(",", nsg_list): {
        rg = rg    # Resource Group
        nsg = nsg  # Network Security Group
      }
    ]
  ])
}

# Turns on flow logs for all network security groups in requested resource groups
resource "azurerm_network_watcher_flow_log" "kentik_network_flow_log" {
  count = length(local.flat_nsgs)

  network_watcher_name = data.azurerm_network_watcher.network_watcher.name
  resource_group_name  = data.azurerm_network_watcher.network_watcher.resource_group_name

  network_security_group_id = local.flat_nsgs[count.index].nsg
  storage_account_id        = azurerm_storage_account.logs_storage_account[index(var.resource_group_names, local.flat_nsgs[count.index].rg)].id
  enabled                   = true
  version                   = 2
  retention_policy {
    enabled = true
    days    = 7
  }
  tags = {
     app = "kentik_flow_log_exporter"
  }
}

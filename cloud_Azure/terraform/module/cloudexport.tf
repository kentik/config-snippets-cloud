terraform {
  required_providers {
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = "~> 0.4"
    }
  }
}

provider "kentik-cloudexport" {
  email = var.email
  token = var.token
}

# Creates one Kentik CloudExport for every requested Resource Group
resource "kentik-cloudexport_item" "azure_export" {
  for_each = { for nsg in local.flat_nsgs : nsg.key => nsg.value }

  name           = "${var.name}-${var.subscription_id}" # resource group name + subscription id make the name unique
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "azure"
  azure {
    subscription_id            = var.subscription_id
    location                   = var.location
    resource_group             = each.value.rg
    storage_account            = azurerm_storage_account.logs_storage_account[each.key].name # storage accounts are mapped 1:1+:1 to nsg(s) and resource_group_names
    security_principal_enabled = true
  }
}

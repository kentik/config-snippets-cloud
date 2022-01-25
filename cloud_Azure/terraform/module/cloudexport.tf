terraform {
  required_providers {
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = ">= 0.4.1"
    }
  }
}

provider "kentik-cloudexport" {
  email = var.email
  token = var.token
}

# Creates one Kentik CloudExport for each requested Resource Group
resource "kentik-cloudexport_item" "azure_export" {
  count = length(var.resource_group_names)

  name           = "${var.name}_${var.resource_group_names[count.index]}" # name must be unique
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "azure"
  azure {
    location                   = var.location
    resource_group             = var.resource_group_names[count.index]
    storage_account            = azurerm_storage_account.logs_storage_account[count.index].name # storage accounts are mapped to resource groups 1:1
    subscription_id            = var.subscription_id
    security_principal_enabled = true
  }
}
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

# Creates Kentik CloudExport for Azure cloud
resource "kentik-cloudexport_item" "azure_export" {
  name           = var.name
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "azure"
  azure {
    location                   = var.location
    resource_group             = var.resource_group_name
    storage_account            = azurerm_storage_account.kentik_storage_account.name
    subscription_id            = var.subscription_id
    security_principal_enabled = true
  }
}
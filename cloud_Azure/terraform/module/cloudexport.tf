terraform {
  required_providers {
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = ">= 0.2.0"
    }
  }
}

resource "kentik-cloudexport_item" "azure_export" {
  # Create only when plan_id is set
  count = var.plan_id == "" ? 0 : 1

  name           = "${var.name}-${terraform.workspace}" # cloudexport name must be unique
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "azure"
  azure {
    location= var.location
    resource_group= var.resource_group_name
    storage_account= azurerm_storage_account.kentik_storage_account.name
    subscription_id= var.subscription_id
    security_principal_enabled=true
  }
}
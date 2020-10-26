terraform {
  required_version = ">= 0.12.0"
}

provider "azurerm" {
  version = "=2.20.0"
  features {}
}

module kentik_azure_integration {
  source  = "../../"
  location = var.location
  resource_group_name = var.resource_group_name
  principal_id = var.principal_id
  subscription_id = var.subscription_id
}

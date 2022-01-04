terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.85.0"
    }
  }
}
 
provider "azurerm" {
  features {}
}


module kentik_azure_integration {
  source  = "../../"
  location = var.location
  resource_group_name = var.resource_group_name
  principal_id = var.principal_id
  subscription_id = var.subscription_id

  plan_id = var.plan_id
  name = var.name
}

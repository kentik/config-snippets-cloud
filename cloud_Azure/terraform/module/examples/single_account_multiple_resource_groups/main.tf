terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 2.85.0"
    }
    azuread = {
      source = "hashicorp/azuread"
      version = ">= 2.14.0"
    }
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = ">= 0.4.1"
    }
  }
}

provider "azurerm" {
  features {}
}

module kentik_azure_integration {
  source  = "../../"
  
  subscription_id = var.subscription_id
  location = var.location
  resource_group_names = var.resource_group_names
  storage_account_names = var.storage_account_names
  email = var.email
  token = var.token
  plan_id = var.plan_id
  name = var.name
}

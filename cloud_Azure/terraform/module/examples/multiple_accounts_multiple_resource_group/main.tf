terraform {
  required_version = "~> 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.85"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.14"
    }
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = "~> 0.4"
    }
  }
}

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.principal_id
  client_secret   = var.principal_secret
}

provider "azuread" {
  tenant_id     = var.tenant_id
  client_id     = var.principal_id
  client_secret = var.principal_secret
}

module "kentik_azure_integration" {
  source = "../../"

  subscription_id       = var.subscription_id
  location              = var.location
  resource_group_names  = var.resource_group_names
  storage_account_names = var.storage_account_names
  resource_tag          = var.resource_tag
  email                 = var.email
  token                 = var.token
  plan_id               = var.plan_id
  name                  = var.name
  description           = var.description
  enabled               = var.enabled
}

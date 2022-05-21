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
}


provider "kentik-cloudexport" {
  email = "dummy@test.mail"
  token = "dummy_token"
}

module "kentik_azure_integration" {
  source = "../"

  subscription_id      = "test_sub_id"
  location             = "westeurope"
  resource_group_names = ["resource-group-1", "resource-group-2"]
  email                = "dummy@test.mail"
  token                = "dummy_token"
  plan_id              = "12345"
  name                 = "azure_europe_west"
}

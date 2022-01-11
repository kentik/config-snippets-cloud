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


provider "kentik-cloudexport" {
  email = "dummy@test.mail"
  token = "dummy_token"
}

module kentik_azure_integration {
  source  = "../"
  location = "westeurope"
  resource_group_name = "testrg"
  subscription_id = "test_sub_id"
  prefix = "test"
  plan_id = "12345"
  name = "azure_europe_west"
}

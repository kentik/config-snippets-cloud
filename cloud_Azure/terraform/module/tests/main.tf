terraform {
  required_version = ">= 0.12.0"
}

provider "azurerm" {
  # whilst the `version` attribute is optional, we recommend pinning to a given version of the Provider
  version = "=2.20.0"
  features {}
}

module kentik_azure_integration {
  source  = "../../"
  location = "westeurope"
  resource_group_name = "test"
  principal_id = "test_prin_id"
  subscription_id = "test_sub_id"
}

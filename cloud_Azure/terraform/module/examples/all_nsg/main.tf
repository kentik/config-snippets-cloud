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
  resource_group_name = "kentik-tf"
  principal_id = "ec113e83-1376-415f-be75-b84ba475066d"
  subscription_id = "414bd5ec-122b-41b7-9715-22f23d5b49c8"
}

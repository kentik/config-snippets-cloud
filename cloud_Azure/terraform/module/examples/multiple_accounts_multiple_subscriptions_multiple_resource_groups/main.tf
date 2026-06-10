terraform {
  required_version = "~> 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.15"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = "~> 0.4"
    }
  }
}

# ---------------------------------------------------------------------------
# Account 1 providers
# One azuread alias per tenant; one azurerm alias per subscription.
# The service principal created by the module is tenant-scoped, so all
# subscriptions in the same tenant share the same azuread alias.
# ---------------------------------------------------------------------------

provider "azuread" {
  alias         = "account1"
  tenant_id     = var.account1_tenant_id
  client_id     = var.account1_client_id
  client_secret = var.account1_client_secret
}

provider "azurerm" {
  alias           = "account1_sub1"
  features        {}
  tenant_id       = var.account1_tenant_id
  subscription_id = var.account1_sub1_id
  client_id       = var.account1_client_id
  client_secret   = var.account1_client_secret
}

provider "azurerm" {
  alias           = "account1_sub2"
  features        {}
  tenant_id       = var.account1_tenant_id
  subscription_id = var.account1_sub2_id
  client_id       = var.account1_client_id
  client_secret   = var.account1_client_secret
}

# ---------------------------------------------------------------------------
# Account 2 providers
# ---------------------------------------------------------------------------

provider "azuread" {
  alias         = "account2"
  tenant_id     = var.account2_tenant_id
  client_id     = var.account2_client_id
  client_secret = var.account2_client_secret
}

provider "azurerm" {
  alias           = "account2_sub1"
  features        {}
  tenant_id       = var.account2_tenant_id
  subscription_id = var.account2_sub1_id
  client_id       = var.account2_client_id
  client_secret   = var.account2_client_secret
}

provider "azurerm" {
  alias           = "account2_sub2"
  features        {}
  tenant_id       = var.account2_tenant_id
  subscription_id = var.account2_sub2_id
  client_id       = var.account2_client_id
  client_secret   = var.account2_client_secret
}

# ---------------------------------------------------------------------------
# Account 1 – Subscription 1
# ---------------------------------------------------------------------------

module "kentik_account1_sub1" {
  source = "../../"
  providers = {
    azurerm = azurerm.account1_sub1
    azuread = azuread.account1
  }

  subscription_id      = var.account1_sub1_id
  location             = var.account1_location
  resource_group_names = var.account1_sub1_resource_group_names
  resource_tag         = var.resource_tag
  email                = var.email
  token                = var.token
  plan_id              = var.plan_id
  name                 = "account1-sub1"
  description          = "Account 1 Subscription 1"
  enabled              = var.enabled
}

# ---------------------------------------------------------------------------
# Account 1 – Subscription 2
# ---------------------------------------------------------------------------

module "kentik_account1_sub2" {
  source = "../../"
  providers = {
    azurerm = azurerm.account1_sub2
    azuread = azuread.account1
  }

  subscription_id      = var.account1_sub2_id
  location             = var.account1_location
  resource_group_names = var.account1_sub2_resource_group_names
  resource_tag         = var.resource_tag
  email                = var.email
  token                = var.token
  plan_id              = var.plan_id
  name                 = "account1-sub2"
  description          = "Account 1 Subscription 2"
  enabled              = var.enabled
}

# ---------------------------------------------------------------------------
# Account 2 – Subscription 1
# ---------------------------------------------------------------------------

module "kentik_account2_sub1" {
  source = "../../"
  providers = {
    azurerm = azurerm.account2_sub1
    azuread = azuread.account2
  }

  subscription_id      = var.account2_sub1_id
  location             = var.account2_location
  resource_group_names = var.account2_sub1_resource_group_names
  resource_tag         = var.resource_tag
  email                = var.email
  token                = var.token
  plan_id              = var.plan_id
  name                 = "account2-sub1"
  description          = "Account 2 Subscription 1"
  enabled              = var.enabled
}

# ---------------------------------------------------------------------------
# Account 2 – Subscription 2
# ---------------------------------------------------------------------------

module "kentik_account2_sub2" {
  source = "../../"
  providers = {
    azurerm = azurerm.account2_sub2
    azuread = azuread.account2
  }

  subscription_id      = var.account2_sub2_id
  location             = var.account2_location
  resource_group_names = var.account2_sub2_resource_group_names
  resource_tag         = var.resource_tag
  email                = var.email
  token                = var.token
  plan_id              = var.plan_id
  name                 = "account2-sub2"
  description          = "Account 2 Subscription 2"
  enabled              = var.enabled
}

# To add more subscriptions: declare a new azurerm provider alias above and
# add a corresponding module block following the same pattern. Subscriptions
# within the same tenant reuse the existing azuread alias for that account.

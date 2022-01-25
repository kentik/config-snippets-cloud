# provideres: azurerm & azuread
variable "location" {
    type = string
    description = "Azure location"
}

variable "subscription_id" {
    type = string
    description = "Azure ubscription ID"
}

variable "resource_group_names" {
    type = list
    description = "List of resource group names to collect flow logs from"
}

variable "prefix" {
    type = string
    description = "Prefix for names of Azure resources created by the module; only lowercase letters and numbers are allowed, max length is 17 characters."
}

# provider: kentik-cloudexport
variable "email" {
  description = "Kentik account email"
  type        = string
}

variable "token" {
  description = "Kentik account token"
  type        = string
}

variable "plan_id" {
  description = "Kentik billing plan ID"
  type        = string
}

variable "name" {
  description = "Cloudexport entry name in Kentik"
  type        = string
}

variable "enabled" {
  description = "Defines if cloud export to Kentik is enabled"
  type        = bool
  default     = true
}

variable "flow_exporter_application_id" {
  type = string
  default = "a20ce222-63c0-46db-86d5-58551eeee89f"
  description = "Kentik NSG Flow Exporter application ID"
}

variable "description" {
  description = "Cloudexport entry description in Kentik"
  type        = string
  default     = "Created using Terraform"
}
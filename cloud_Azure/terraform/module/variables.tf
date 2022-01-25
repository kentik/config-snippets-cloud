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
    description = "Unique prefix to be used for resource creation; can only consist of lowercase letters and numbers"
}

# provider: kentik-cloudexport
variable "plan_id" {
  description = "Kentik billing plan ID"
  type        = string
}

variable "name" {
  description = "Exported cloud name in Kentik Portal"
  type        = string
}

variable "flow_exporter_application_id" {
  type = string
  default = "a20ce222-63c0-46db-86d5-58551eeee89f"
  description = "Kentik NSG Flow Exporter application ID"
}

variable "enabled" {
  description = "Defines if cloud exported to Kentik is enabled"
  type        = bool
  default     = true
}

variable "description" {
  description = "Description of exported cloud in Kentik Portal"
  type        = string
  default     = ""
}
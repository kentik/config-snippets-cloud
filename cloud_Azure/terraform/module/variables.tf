# provideres: azurerm & azuread
variable "subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "location" {
  type        = string
  description = "Azure location"
}

variable "resource_group_names" {
  type        = list(string)
  description = "Names of Resource Groups from which to collect flow logs"
}

variable "storage_account_names" {
  type        = list(string)
  description = "Storage Account names to store the flow logs in. They must meet Azure Storage Account naming restrictions. There should be either one Storage Account name per Resource Group name, or none (in that case, names will be generated)"
  default     = []
}

variable "resource_tag" {
  type        = string
  description = "Azure Tag value to apply to created resources"
  default     = "flow_log_exporter"
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

variable "description" {
  description = "Cloudexport entry description in Kentik"
  type        = string
  default     = "Created using Terraform"
}

variable "enabled" {
  description = "Defines if cloud export to Kentik is enabled"
  type        = bool
  default     = true
}

variable "flow_exporter_application_id" {
  type        = string
  default     = "a20ce222-63c0-46db-86d5-58551eeee89f"
  description = "Kentik NSG Flow Exporter application ID"
}
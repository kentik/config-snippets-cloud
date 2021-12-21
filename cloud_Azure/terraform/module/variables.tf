# azurerm
variable "location" {
    type = string
    description = "Azure location"
}

variable "subscription_id" {
    type = string
    description = "Subscription Id"
}

variable "resource_group_name" {
    type = string
    description = "Resource group name"
}

variable "principal_id" {
    type = string
    description = "Service Principal Id"
}

variable "prefix" {
    type = string
    default = "kentik"
    description = "Prefix to be used for resource creation - default \"kentik\""
}

# cloudexport
variable "plan_id" {
  description = "Billing plan ID"
  type        = string
}

variable "name" {
  description = "Exported cloud name in Kentik Portal"
  type        = string
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
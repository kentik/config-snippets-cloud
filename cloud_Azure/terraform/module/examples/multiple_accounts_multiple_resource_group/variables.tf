variable "subscription_id" {
    type = string
    description = "Azure subscription ID"
}

variable "tenant_id" {
    type = string
    description = "Azure tenant ID"
}

variable "principal_id" {
    type = string
    description = "Azure service principal ID"
}

variable "principal_secret" {
    type = string
    description = "Azure service principal secret (aka password)"
}

variable "location" {
    type = string
    description = "Azure location"
}

variable "resource_group_names" {
    type = list(string)
    description = "List of Azure resource group names"
}

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
}

variable "enabled" {
  description = "Defines if cloud export to Kentik is enabled"
  type        = bool
}
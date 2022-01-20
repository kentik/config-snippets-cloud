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

variable "email" {
  description = "Kentik account email"
  type        = string
}

variable "token" {
  description = "Kentik account token"
  type        = string
}

variable "prefix" {
    type = string
    description = "Prefix for names of Azure resources created by the module; only lowercase letters and numbers are allowed, max length is 17 characters."
}
variable "plan_id" {
  description = "Billing plan ID"
  type        = string
}

variable "name" {
  description = "Cloudexport entry name in Kentik"
  type        = string
}
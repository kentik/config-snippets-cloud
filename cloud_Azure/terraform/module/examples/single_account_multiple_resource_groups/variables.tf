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
  description = "Names of Storage Accounts for storing flow logs. Names must meet Azure Storage Account naming restrictions. The list should either contain 1 Storage Account name for each Resource Group, or be empty, in which case names will be generated automatically"
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
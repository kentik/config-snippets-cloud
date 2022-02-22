variable "subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "tenant_id" {
  type        = string
  description = "Azure tenant ID"
}

variable "principal_id" {
  type        = string
  description = "Azure service principal ID"
}

variable "principal_secret" {
  type        = string
  description = "Azure service principal secret (aka password)"
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

variable "resource_tag" {
  type        = string
  description = "Azure Tag value to apply to created resources"
  default     = "flow_log_exporter"
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
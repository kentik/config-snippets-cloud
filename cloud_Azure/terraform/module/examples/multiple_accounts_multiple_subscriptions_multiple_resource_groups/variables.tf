# ---------------------------------------------------------------------------
# Kentik credentials (shared across all accounts)
# ---------------------------------------------------------------------------

variable "email" {
  description = "Kentik account email"
  type        = string
}

variable "token" {
  description = "Kentik account token"
  type        = string
  sensitive   = true
}

variable "plan_id" {
  description = "Kentik billing plan ID"
  type        = string
}

variable "enabled" {
  description = "Enable or disable cloud exports to Kentik"
  type        = bool
  default     = true
}

variable "resource_tag" {
  description = "Azure tag value applied to resources created by this module"
  type        = string
  default     = "flow_log_exporter"
}

# ---------------------------------------------------------------------------
# Account 1
# ---------------------------------------------------------------------------

variable "account1_tenant_id" {
  description = "Azure tenant ID for Account 1"
  type        = string
}

variable "account1_client_id" {
  description = "Service principal client ID for Account 1"
  type        = string
}

variable "account1_client_secret" {
  description = "Service principal client secret for Account 1"
  type        = string
  sensitive   = true
}

variable "account1_location" {
  description = "Azure location for Account 1 resources (e.g. eastus)"
  type        = string
}

variable "account1_sub1_id" {
  description = "Subscription ID for Account 1, Subscription 1"
  type        = string
}

variable "account1_sub1_resource_group_names" {
  description = "Resource groups to monitor in Account 1, Subscription 1"
  type        = list(string)
}

variable "account1_sub2_id" {
  description = "Subscription ID for Account 1, Subscription 2"
  type        = string
}

variable "account1_sub2_resource_group_names" {
  description = "Resource groups to monitor in Account 1, Subscription 2"
  type        = list(string)
}

# ---------------------------------------------------------------------------
# Account 2
# ---------------------------------------------------------------------------

variable "account2_tenant_id" {
  description = "Azure tenant ID for Account 2"
  type        = string
}

variable "account2_client_id" {
  description = "Service principal client ID for Account 2"
  type        = string
}

variable "account2_client_secret" {
  description = "Service principal client secret for Account 2"
  type        = string
  sensitive   = true
}

variable "account2_location" {
  description = "Azure location for Account 2 resources (e.g. westeurope)"
  type        = string
}

variable "account2_sub1_id" {
  description = "Subscription ID for Account 2, Subscription 1"
  type        = string
}

variable "account2_sub1_resource_group_names" {
  description = "Resource groups to monitor in Account 2, Subscription 1"
  type        = list(string)
}

variable "account2_sub2_id" {
  description = "Subscription ID for Account 2, Subscription 2"
  type        = string
}

variable "account2_sub2_resource_group_names" {
  description = "Resource groups to monitor in Account 2, Subscription 2"
  type        = list(string)
}

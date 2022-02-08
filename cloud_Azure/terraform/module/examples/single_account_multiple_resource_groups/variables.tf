variable "subscription_id" {
    type = string
    description = "Azure subscription ID"
}

variable "location" {
    type = string
    description = "Azure location"
}

variable "resource_group_names" {
    type = list(string)
    description = "Resource Group names for which flow logs are to be collected"
}

variable "storage_account_names" {
    type = list(string)
    description = "Storage Account names to store the flow logs in. They must meet Azure Storage Account naming restrictions. There should be either one Storage Account name per Resource Group name, or none (in that case, names will be generated)"
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
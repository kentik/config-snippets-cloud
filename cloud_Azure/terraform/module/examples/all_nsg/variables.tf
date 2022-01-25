variable "location" {
    type = string
    description = "Azure location"
}

variable "subscription_id" {
    type = string
    description = "Subscription Id"
}

variable "resource_group_names" {
    type = list
    description = "List of resource group names"
}

variable "prefix" {
    type = string
    description = "Unique prefix to be used for resource creation; can only consist of lowercase letters and numbers, max length is 17"
}
variable "plan_id" {
  description = "Billing plan ID"
  type        = string
}

variable "name" {
  description = "Cloudexport entry name in Kentik"
  type        = string
}
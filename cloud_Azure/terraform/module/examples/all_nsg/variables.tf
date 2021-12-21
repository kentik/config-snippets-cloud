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

# cloudexport
variable "plan_id" {
  description = "Billing plan ID"
  type        = string
}

variable "name" {
  description = "Exported cloud name in Kentik Portal"
  type        = string
}
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
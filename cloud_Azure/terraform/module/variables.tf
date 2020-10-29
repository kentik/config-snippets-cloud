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

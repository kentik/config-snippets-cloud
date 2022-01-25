variable "project" {
    type = string
    description = "GCP project where subnets are created"
}

variable "region" {
    type = string
    description = "Subnets region"
}

variable "credentials" {
    type = string
    description = "Path to credentials"
}

variable "network" {
  description = "Network name to pull subnets from"
  type        = string
}

variable "name" {
  description = "Cloudexport entry name in Kentik"
  type = string
  default = "terraform_gcp_exported_cloud"
}

variable "description" {
  description = "Cloudexport entry description in Kentik"
  type = string
  default = ""
}

variable "plan_id" {
  description = "Billing plan ID"
  type = string
}

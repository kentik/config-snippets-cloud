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
  description = "Exported cloud name in Kentik Portal"
  type = string
  default = "terraform_aws_exported_cloud"
}

variable "description" {
  type = string
  default = ""
}

variable "plan_id" {
  description = "Billing plan ID"
  type = string
}

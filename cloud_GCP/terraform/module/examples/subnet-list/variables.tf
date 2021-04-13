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

variable "subnet_names" {
  description = "List of subnets names for which Kentik should gather logs"
  type        = list(string)
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

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

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

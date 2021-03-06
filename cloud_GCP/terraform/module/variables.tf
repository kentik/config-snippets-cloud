variable "subnets_names_list" {
  description = "List of subnets names for which Kentik should gather logs"
  type        = list(string)
  default     = [""]
}

variable "topic_prefix" {
  description = "Pub/Sub topic prefix and subscription prefix"
  type        = string
  default     = "kentik"
}

variable "sink_prefix" {
  description = "Prefix to use with logs sink"
  type        = string
  default     = "kentik_pubsub"
}

variable "region" {
  description = "Subnets region"
  type        = string
}

variable "name" {
  description = "Exported cloud name in Kentik Portal"
  type = string
  default = "terraform_aws_exported_cloud"
}

variable "enabled" {
  description = "Defines if cloud exported to Kentik is enabled"
  type        = bool
  default     = true
}

variable "description" {
  description = "Description of exported cloud in Kentik Portal"
  type = string
  default = ""
}

variable "plan_id" {
  description = "Billing plan ID"
  type = string
}

variable "project" {
  description = "GCP project name"
  type = string
}

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
  description = "Cloudexport entry name in Kentik"
  type = string
  default = "terraform_gcp_exported_cloud"
}

variable "enabled" {
  description = "Defines if cloud exported to Kentik is enabled"
  type        = bool
  default     = true
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

variable "project" {
  description = "GCP project name"
  type = string
}

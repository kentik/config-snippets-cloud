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
  default     = "kentik_pubsub_sink"
}

variable "region" {
  description = "Subnets region"
  type        = string
}
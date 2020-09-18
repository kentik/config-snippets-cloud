variable "region" {
  type    = string
  default = "us-east-1"
}

variable "cluster_name" {
  type    = string
  default = "boutique-k8s-kentik"
}

variable "worker_node_type" {
  type    = string
  default = "t3a.medium"
}

variable "worker_node_count" {
  type    = number
  default = 2
}

variable "k8s_version" {
  type    = string
  default = "1.17"
}

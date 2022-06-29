variable "key_name" {
  description = "Key name of the Key Pair to use for the instance"
  type        = string
  default     = ""
}

variable "iam_instance_profile" {
  description = "IAM role ID"
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "Subnet ID"
  type        = string
  default     = ""
}

variable "vpc_security_group_ids" {
  description = "List of security groups IDs"
  type        = list(string)
  default     = [""]
}

variable "plan_id" {
  description = "Kentik plan ID"
  type        = string
  default     = ""
}
variable "region" {
  type        = string
}

variable "plan_id" {
  type        = string
}

variable "bucket_region_name" {
  type        = list(list(string))
  default     = []
  description = "internal use only"
}

variable "bucket_arn_list" {
  type        = list(string)
  default     = null
  description = "internal use only"
}

variable "iam_role_prefix" {
  type = string
  default = "tf-multi-region"
}

variable "external_id" {
  type        = string
}
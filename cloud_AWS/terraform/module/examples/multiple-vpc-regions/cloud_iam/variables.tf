variable "region" {
  type        = string
}

variable "plan_id" {
  type        = string
  default = ""
}

variable "bucket_region_name" {
  type        = list(list(string))
  default     = []
}

variable "bucket_arn_list" {
  type        = list(string)
  default     = null
}

variable "iam_role_prefix" {
  type = string
  default = "tf-multi-region"
}

variable "external_id" {
  type        = string
  default     = ""
}
variable "vpc_id_list" {
  type        = list(string)
}

variable "region" {
  type        = string
}

variable "s3_bucket_prefix" {
  type = string
  default = "tf-multi-region"
}
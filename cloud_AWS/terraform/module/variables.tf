variable "rw_s3_access" {
  description = "If set to true, Kentik platform will be able to delete old logs from s3 bucket"
  type        = bool
}

variable "vpc_id_list" {
  description = "List of VPC ids for which Kentik should gather logs"
  type        = list(string)
  default     = [""]
}

variable "s3_bucket_prefix" {
  description = "Prefix to use with s3 bucket name"
  type        = string
  default     = "kentik"
}

variable "s3_use_one_bucket" {
  description = "If we should use one or more buckets"
  type        = bool
  default     = true
}

variable "s3_flowlogs_path" {
  description = "Path on the S3 bucket for saving logs"
  type        = string
  default     = ""
}

variable "s3_base_name" {
  description = "Base name for s3 bucket. Used in single bucket mode"
  type        = string
  default     = "ingest-bucket"
}

variable "s3_delete_nonempty_buckets" {
  description = "Delete bucket even if it is not empty"
  type        = bool
  default     = false
}

variable "iam_role_prefix" {
  description = "Prefix to use with IAM roles"
  type        = string
  default     = "Kentik"
}

variable "store_logs_more_frequently" {
  description = "Adds option to store data in 1 minute interval (default is 10 minutes)"
  type        = bool
  default     = false
}

variable "create_role" {
  description = "If set to false it will not create kentik_role"
  type        = bool
  default     = true
}

variable "name" {
  description = "Cloudexport entry name in Kentik"
  type        = string
  default     = "terraform_aws_exported_cloud"
}

variable "enabled" {
  description = "Defines if cloud exported to Kentik is enabled"
  type        = bool
  default     = true
}

variable "description" {
  description = "Cloudexport entry description in Kentik"
  type        = string
  default     = ""
}

variable "plan_id" {
  description = "Billing plan ID"
  type        = string
  default     = ""
}

variable "delete_after_read" {
  type    = bool
  default = false
}

variable "multiple_buckets" {
  type    = bool
  default = false
}

variable "region" {
  description = "Specifies AWS region passed to kentik-cloudexport provider"
  type        = string
}

variable "external_id" {
  description = "Company ID assigned by Kentik passed to assume role policy of TerraformIngestRole."
  type        = string
  default     = ""
}

variable bucket_arn_list {
  description = "List of all created buckets arn's - internal use only"
  type        = list(string)
  default     = null
}

variable "create_bucket" {
  type    = bool
  default = true
}

variable "bucket_region_name" {
  description = "List of all created buckets names - internal use only"
  type        = list(list(string))
  default     = []
}

variable "create_cloudexport" {
  description = "If set to false it will not create CloudExport"
  type    = bool
  default = true
}

# OCI identity
variable "tenancy_id" {
  description = "OCI Tenancy OCID"
  type        = string
}

variable "compartment_id" {
  description = "OCI Compartment OCID where resources will be created. Defaults to tenancy root if not set."
  type        = string
  default     = ""
}

variable "region" {
  description = "OCI region (e.g. us-ashburn-1)"
  type        = string
}

# VCNs to monitor
variable "vcn_id_list" {
  description = "List of VCN OCIDs for which Kentik should gather flow logs"
  type        = list(string)
}

# Object Storage
variable "bucket_name_prefix" {
  description = "Prefix for the Object Storage bucket name"
  type        = string
  default     = "kentik"
}

variable "object_name_prefix" {
  description = "Prefix for flow log objects stored in the bucket"
  type        = string
  default     = "flow-logs"
}

# IAM
variable "create_user" {
  description = "If true, creates an OCI IAM user for Kentik access. Set to false when using a cross-tenancy policy."
  type        = bool
  default     = true
}

variable "iam_prefix" {
  description = "Prefix for IAM resource names (user, group, policy)"
  type        = string
  default     = "kentik"
}

variable "kentik_user_email" {
  description = "Email address for the OCI IAM user created for Kentik access. Required when create_user is true."
  type        = string
  default     = ""
}

variable "kentik_api_public_key" {
  description = "Kentik public key for OCI API authentication. Required when create_user is true. Obtain from Kentik portal."
  type        = string
  default     = ""
  sensitive   = true
}

# Flow logs
variable "flow_log_sampling_rate" {
  description = "Flow log sampling rate as a percentage (1-100). 100 captures all traffic."
  type        = number
  default     = 100
}

variable "log_prefix" {
  description = "Prefix for Log Group, capture filter, and log resource names"
  type        = string
  default     = "kentik"
}

# Kentik cloudexport
variable "name" {
  description = "Cloudexport entry name in Kentik"
  type        = string
  default     = "terraform_oci_exported_cloud"
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
  description = "Kentik billing plan ID"
  type        = string
  default     = ""
}

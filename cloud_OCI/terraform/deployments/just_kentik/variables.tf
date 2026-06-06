# OCI provider authentication
variable "oci_user_id" {
  description = "OCID of the OCI user used to authenticate the Terraform provider"
  type        = string
}

variable "oci_fingerprint" {
  description = "Fingerprint of the API key used by the OCI Terraform provider"
  type        = string
}

variable "oci_private_key_path" {
  description = "Path to the private key file used by the OCI Terraform provider"
  type        = string
}

# OCI tenancy / compartment
variable "tenancy_id" {
  description = "OCI Tenancy OCID"
  type        = string
}

variable "compartment_id" {
  description = "OCI Compartment OCID where resources will be created. Leave empty to use the tenancy root."
  type        = string
  default     = ""
}

variable "region" {
  description = "OCI region (e.g. us-ashburn-1)"
  type        = string
}

# VCNs
variable "vcn_id_list" {
  description = "List of VCN OCIDs for which Kentik should gather flow logs"
  type        = list(string)
}

# IAM
variable "create_user" {
  description = "If true, creates an OCI IAM user for Kentik access"
  type        = bool
  default     = true
}

variable "iam_prefix" {
  description = "Prefix for IAM resource names"
  type        = string
  default     = "kentik"
}

variable "kentik_user_email" {
  description = "Email address for the OCI IAM user created for Kentik access"
  type        = string
  default     = ""
}

variable "kentik_api_public_key" {
  description = "Kentik public key for OCI API authentication (from Kentik portal)"
  type        = string
  default     = ""
  sensitive   = true
}

# Kentik
variable "name" {
  description = "Cloudexport entry name in Kentik"
  type        = string
  default     = "terraform_oci_exported_cloud"
}

variable "description" {
  description = "Cloudexport entry description in Kentik"
  type        = string
  default     = "Created using Terraform"
}

variable "plan_id" {
  description = "Kentik billing plan ID"
  type        = string
  default     = ""
}

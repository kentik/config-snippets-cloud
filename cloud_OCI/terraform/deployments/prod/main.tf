terraform {
  required_version = "~> 1.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = "~> 0.4"
    }
  }
}

provider "oci" {
  tenancy_ocid     = var.tenancy_id
  user_ocid        = var.oci_user_id
  fingerprint      = var.oci_fingerprint
  private_key_path = var.oci_private_key_path
  region           = var.region
}

provider "kentik-cloudexport" {
  # email and token are read from KTAPI_AUTH_EMAIL and KTAPI_AUTH_TOKEN env variables
}

module "kentik_oci_integration" {
  source = "../../module/"

  tenancy_id     = var.tenancy_id
  compartment_id = var.compartment_id
  region         = var.region
  vcn_id_list    = var.vcn_id_list

  iam_prefix            = var.iam_prefix
  create_user           = var.create_user
  kentik_user_email     = var.kentik_user_email
  kentik_api_public_key = var.kentik_api_public_key

  name        = var.name
  description = var.description
  plan_id     = var.plan_id
}

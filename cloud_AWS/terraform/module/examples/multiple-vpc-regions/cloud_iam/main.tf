terraform {
  required_version = "~> 1.0"
  required_providers {
    aws = {
      version = "~> 4.0"
    }
    kentik-cloudexport = {
      version = "~> 0.4"
      source  = "kentik/kentik-cloudexport"
    }
  }
}


module "role_and_cloud_export" {
  // Use the module from local filesystem
  source = "../../../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  create_bucket = false
  create_role = true

  region                     = var.region
  rw_s3_access               = true
  iam_role_prefix            = var.iam_role_prefix
  name                       = "example-multivpc-tf"
  plan_id                    = var.plan_id
  external_id                = var.external_id
  bucket_region_name         = var.bucket_region_name
  bucket_arn_list            = var.bucket_arn_list
}

terraform {
  required_version = "~> 1.0"
  required_providers {
    aws = {
      version = "~> 4.0"
    }
  }
}

module "s3_bucket_resources" {
  // Use the module from local filesystem
  source = "../../../"

  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"
  create_bucket = true
  create_role = false

  s3_use_one_bucket          = false
  rw_s3_access               = true
  vpc_id_list                = var.vpc_id_list
  s3_bucket_prefix           = var.s3_bucket_prefix
  s3_delete_nonempty_buckets = true
  store_logs_more_frequently = true
  region                     = var.region

}
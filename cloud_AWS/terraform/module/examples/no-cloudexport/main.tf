terraform {
  required_version = ">= 0.12.0"
  required_providers {
    aws = {
      version = ">= 2.28.1"
    }
    kentik-cloudexport = {
      version = ">= 0.2.0"
      source  = "kentik/kentik-cloudexport"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

provider "kentik-cloudexport" {
  email = "dummy"
  token = "dummy"
}

module "kentik_aws_integration" {
  // Use the module from local filesystem
  source = "../../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  region                     = "us-east-2"
  rw_s3_access               = true
  vpc_id_list                = [var.vpc_id]
  s3_bucket_prefix           = "terraform-example"
  s3_delete_nonempty_buckets = true
  iam_role_prefix            = "terraform-example"
  store_logs_more_frequently = true
}

terraform {
  required_version = ">= 0.12.0"
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

provider "aws" {
  region = "us-east-2"
}

provider "kentik-cloudexport" {}

module "kentik_aws_integration" {
  // Use the module from local filesystem
  source = "../../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  rw_s3_access               = true
  vpc_id_list                = [var.vpc_id]
  s3_bucket_prefix           = "terraform-example"
  s3_delete_nonempty_buckets = true
  iam_role_prefix            = "terraform-example"
  store_logs_more_frequently = true
  name                       = "example-aws-terraform-name"
  plan_id                    = "11467"
  region                     = "us-east-2"
  // The company ID passed here can be obtained in automated configuration of AWS cloudexport
  // (https://portal.kentik.com/v4/setup/clouds/aws).
  external_id = "74333"
}

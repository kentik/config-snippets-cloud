terraform {
  required_version = ">= 0.12.0"
  required_providers {
    aws = {
      version = ">= 2.28.1, < 4.0.0"
    }
    kentik-cloudexport = {
      version = ">= 0.2.0"
      source  = "kentik/kentik-cloudexport"
    }
  }
}

provider "aws" {
  region = var.region
}

provider "kentik-cloudexport" {}


data "aws_vpcs" "id_list" {}

module "kentik_aws_integration" {
  // Use the module from local filesystem
  source = "../../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  rw_s3_access               = true
  vpc_id_list                = data.aws_vpcs.id_list.ids
  s3_bucket_prefix           = "terraform-example"
  s3_delete_nonempty_buckets = true
  iam_role_prefix            = "terraform-example"
  store_logs_more_frequently = true
  name                       = "example-aws-terraform-name"
  region                     = var.region

  // The company ID passed here can be obtained in automated configuration of AWS cloudexport
  // (https://portal.kentik.com/v4/setup/clouds/aws).
  external_id                = "74333"
  plan_id                    = "11467"
}

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

provider "kentik-cloudexport" {}

module "kentik_aws_integration" {
  // Use the module from local filesystem
  source = "../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  rw_s3_access               = true
  vpc_id_list                = ["vpc-019526f2f3408e2eb"]
  s3_bucket_prefix           = "terraform-demo-show"
  iam_role_prefix            = "terraform-demo-show"
  store_logs_more_frequently = true
  name                       = "terraform-demo-show"
  plan_id                    = "11467"
  region                     = "us-east-2"
}

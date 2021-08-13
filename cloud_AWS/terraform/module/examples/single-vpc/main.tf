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

  # Allow module to assume role with external ID
  //  assume_role {
  //    role_arn     = "arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME"
  //    external_id = "a43dd248-0047-11ec-ab2e-6b5423aa2e8a"
  //  }
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
  iam_role_prefix            = "terraform-example"
  store_logs_more_frequently = true
  name                       = "example-aws-terraform-name"
  plan_id                    = "11467"
  region                     = "us-east-2"
  external_id                = "a43dd248-0047-11ec-ab2e-6b5423aa2e8a"
}

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
  # email, token and apiurl are read from KTAPI_AUTH_EMAIL, KTAPI_AUTH_TOKEN, KTAPI_URL env variables
}

module "kentik_aws_integration" {
  source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  rw_s3_access = true
  vpc_id_list = ["vpc-019526f2f3408e2eb"]
  s3_bucket_prefix           = "terraform-demo-show"
  iam_role_prefix            = "terraform-demo-show" 
  store_logs_more_frequently = true
  name                       = "terraform-demo-show"
  plan_id                    = "11467"
  region                     = "us-east-2"
}


## Configure AWS provider to use LocalStack
terraform {
  required_version = ">= 0.12.0"
  required_providers {
    aws = {
      version = "~> 4.0"
    }
    kentik-cloudexport = {
      version = ">= 0.2.0"
      source  = "kentik/kentik-cloudexport"
    }
  }
}

provider "aws" {
  region  = "us-east-1"

  access_key = "dump-access-key"
  secret_key = "dump-secret-key"

  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true

  s3_use_path_style  = true

  endpoints {
    iam = "http://localstack:4566"
    s3  = "http://localstack:4566"
    ec2 = "http://localstack:4566"
  }
}

provider "kentik-cloudexport" {
  email = "dummy@test.mail"
  token = "dummy_token"
}

## Create VPC ##
resource "aws_vpc" "test-vpc" {
  count                            = 3
  cidr_block                       = "10.0.0.0/16"
  assign_generated_ipv6_cidr_block = true
}

## Use module for single-vpc integration ##
module "single_vpc_integration" {
  source                     = "../"
  vpc_id_list                = [aws_vpc.test-vpc.0.id]
  rw_s3_access               = true
  store_logs_more_frequently = false
  s3_bucket_prefix           = "single"
  region                     = "us-east-1"
  plan_id                    = "11467"
}

## Use module for multi-vpc integration ##
module "multi_vpc_integration" {
  source                     = "../"
  vpc_id_list                = [aws_vpc.test-vpc.1.id, aws_vpc.test-vpc.2.id]
  rw_s3_access               = true
  store_logs_more_frequently = true
  s3_bucket_prefix           = "multi"
  region                     = "us-east-1"
  plan_id                    = "11467"
}

terraform {
  required_version = ">= 0.12.0"
}

provider "aws" {
  version = ">= 2.28.1"
  region  = "us-east-2"
}

data "aws_vpcs" "all-vpc" {}

module "kentik_aws_integration" {
  source = "../../"

  rw_s3_access = true
  vpc_id_list = data.aws_vpcs.all-vpc.ids
}

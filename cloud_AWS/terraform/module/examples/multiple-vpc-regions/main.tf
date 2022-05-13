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

module "kentik_aws_integration_vpc1" {
  // Use the module from local filesystem
  source = "../../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  providers = {
    aws = aws.us-e1
  }
  rw_s3_access               = true
  vpc_id_list                = [var.vpc_id_1]
  s3_bucket_prefix           = "terraform-example-1"
  s3_delete_nonempty_buckets = true
  store_logs_more_frequently = true
  region                     = "us-east-1"
  create_role = false
}

module "kentik_aws_integration_vpc2" {
  // Use the module from local filesystem
  source = "../../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  providers = {
    aws = aws.eu-c1
  }

  rw_s3_access               = true
  vpc_id_list                = [var.vpc_id_2]
  s3_bucket_prefix           = "terraform-example-2"
  s3_delete_nonempty_buckets = true
  store_logs_more_frequently = true
  region                     = "eu-central-1"
  create_role = false
}

module "role_and_cloud_export" {
  // Use the module from local filesystem
  source = "../../"
  // Use the module from Github
  // source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  create_bucket = false

  region                     = "us-east-1"
  regions                    = concat(module.kentik_aws_integration_vpc1.regions, module.kentik_aws_integration_vpc2.regions)
  rw_s3_access               = true
  iam_role_prefix            = "terraform-example"
  name                       = "example-aws-terraform-name-eu"
  plan_id                    = "11467"
  external_id = "74333"
  bucket_arn_list = concat(module.kentik_aws_integration_vpc1.bucket_arn_list, module.kentik_aws_integration_vpc2.bucket_arn_list)
  bucket_name_list = concat(module.kentik_aws_integration_vpc1.bucket_name_list, module.kentik_aws_integration_vpc2.bucket_name_list)
}

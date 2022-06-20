terraform {
  required_version = ">= 0.12.0"
}

# tflint-ignore: terraform_module_version
provider "aws" {
  version = ">= 2.28.1"
  region  = "us-west-1"
}

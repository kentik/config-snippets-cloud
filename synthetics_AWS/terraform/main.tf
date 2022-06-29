terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      version = ">= 4.7"
    }
  }
}

provider "aws" {
  region  = "us-east-2"
}
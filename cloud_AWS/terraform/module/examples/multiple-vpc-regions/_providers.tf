provider "kentik-cloudexport" {}

provider "aws" {
  alias = "us-e1"
  region = "us-east-1"
}

provider "aws" {
  alias = "eu-c1"
  region = "eu-central-1"
}
## Configure AWS provider to use LocalStack
terraform {
  required_version = ">= 0.12.0"
}

provider "google" {
  version = ">= 3.41.0"
  credentials = file("${var.credentials}")
  project     = var.project
  region      = var.region
}

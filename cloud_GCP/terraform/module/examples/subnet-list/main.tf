terraform {
  required_version = ">= 0.12.0"
}

provider "google" {
  version = ">= 3.41.0"
  credentials = file("${var.credentials}")
  project     = var.project
  region      = var.region
}

module "kentik_gcp_integration" {
  source = "../../"
  subnets_names_list = var.subnet_names
  region = var.region
}

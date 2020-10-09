## Configure GCP provider for tests
terraform {
  required_version = ">= 0.12.0"
}

provider "google" {
  version = ">= 3.41.0"
  project     = "test-project"
  region      = "europe-west1"
}

module "kentik_gcp_integration" {
  source = "../"
  subnets_names_list = ["test-name"]
  region = "europe-west1"
}

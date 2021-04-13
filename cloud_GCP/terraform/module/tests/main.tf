## Configure GCP provider for tests
terraform {
  required_version = ">= 0.12.0"
  required_providers {
    google = {
      version = ">= 3.41.0"
    }
    kentik-cloudexport = {
      version = "0.1.0"
      source = "kentik/kentik-cloudexport"
    }
  }
}

provider "google" {
  project     = "test-project"
  region      = "europe-west1"
}

provider "kentik-cloudexport" {

}

module "kentik_gcp_integration" {
  source = "../"
  subnets_names_list = ["test-name"]
  region = "europe-west1"
}

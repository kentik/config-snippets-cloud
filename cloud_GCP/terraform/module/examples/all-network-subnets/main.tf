terraform {
  required_version = "~> 1.0"
  required_providers {
    google = {
      version = "~> 4.0"
    }
    kentik-cloudexport = {
      version = "~> 0.4"
      source = "kentik/kentik-cloudexport"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

provider "kentik-cloudexport" {
  # email, token and apiurl are read from KTAPI_AUTH_EMAIL, KTAPI_AUTH_TOKEN, KTAPI_URL env variables
}

data "google_compute_network" "network" {
  name = var.network
}

data "google_compute_subnetwork" "subnetworks" {
  count  = length(data.google_compute_network.network.subnetworks_self_links)
  name = element(split("/", data.google_compute_network.network.subnetworks_self_links[count.index]), 10)
}

module "kentik_gcp_integration" {
  source             = "../../"
  subnets_names_list = [ for subnet in data.google_compute_subnetwork.subnetworks : subnet.name ]
  region = var.region
  project = var.project
  name = var.name
  description = var.description
  plan_id = var.plan_id
}

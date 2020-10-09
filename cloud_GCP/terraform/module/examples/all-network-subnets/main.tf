terraform {
  required_version = ">= 0.12.0"
}

provider "google" {
  version = ">= 3.41.0"
  credentials = file("${var.credentials}")
  project     = var.project
  region      = var.region
}

data "google_compute_network" "network" {
  name = var.network
}

data "google_compute_subnetwork" "subnetworks" {
  count  = "${length(data.google_compute_network.network.subnetworks_self_links)}"
  name = "${element(split("/", data.google_compute_network.network.subnetworks_self_links[count.index]), 10)}"
}

module "kentik_gcp_integration" {
  source = "../../"
  subnets_names_list = [ for subnet in data.google_compute_subnetwork.subnetworks : subnet.name ]
  region = var.region
}

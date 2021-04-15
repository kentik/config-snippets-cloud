data "google_compute_network" "network" {
  name = var.network
}

data "google_compute_subnetwork" "subnetworks" {
  count  = length(data.google_compute_network.network.subnetworks_self_links)
  name = element(split("/", data.google_compute_network.network.subnetworks_self_links[count.index]), 10)
}

module "kentik_gcp_integration" {
  source             = "../../cloud_GCP/terraform/module"
  subnets_names_list = [ for subnet in data.google_compute_subnetwork.subnetworks : subnet.name ]
  region = var.region
  project = var.project
  name = var.name
  description = var.description
  plan_id = var.plan_id
}

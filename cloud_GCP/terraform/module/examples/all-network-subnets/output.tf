output "kentik_subscription" {
  value = module.kentik_gcp_integration.subscription
}

output "project" {
  value = var.project
}

output "subnets" {
  value = [ for s in data.google_compute_subnetwork.subnetworks : s.name ]
}

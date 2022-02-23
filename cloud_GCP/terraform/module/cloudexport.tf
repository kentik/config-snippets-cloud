terraform {
  required_providers {
    kentik-cloudexport = {
      source = "kentik/kentik-cloudexport"
      version = "~> 0.4"
    }
  }
}

resource "kentik-cloudexport_item" "gce_export" {
  name           = var.name
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "gce"
  gce {
    project      = var.project
    subscription = google_pubsub_subscription.kentik_topic_subscription.name
  }
}

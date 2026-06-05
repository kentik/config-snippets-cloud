terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = "~> 0.4"
    }
  }
}

resource "kentik-cloudexport_item" "oci" {
  # Create only when plan_id is set
  count = var.plan_id == "" ? 0 : 1

  name           = "${var.name}-${terraform.workspace}"
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "CLOUD_PROVIDER_OCI"
}

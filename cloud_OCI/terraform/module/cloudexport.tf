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
  oci {
    user_id                  = var.create_user ? oci_identity_user.kentik_user[0].id : ""
    tenancy_id               = var.tenancy_id
    compartment_id           = local.compartment_id
    default_region           = var.region
    collect_flow_logs        = true
    bucket_name              = oci_objectstorage_bucket.kentik_logs.name
    bucket_namespace_name    = data.oci_objectstorage_namespace.ns.namespace
    service_connector_ocid   = oci_sch_service_connector.kentik_connector.id
    flow_object_name_prefix  = var.object_name_prefix
  }
}

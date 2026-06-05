resource "oci_sch_service_connector" "kentik_connector" {
  compartment_id = local.compartment_id
  display_name   = "${var.log_prefix}-flow-logs-connector"

  source {
    kind = "logging"
    log_sources {
      compartment_id = local.compartment_id
      log_group_id   = oci_logging_log_group.kentik_log_group.id
    }
  }

  target {
    kind                       = "objectStorage"
    bucket                     = oci_objectstorage_bucket.kentik_logs.name
    namespace                  = data.oci_objectstorage_namespace.ns.namespace
    object_name_prefix         = var.object_name_prefix
    batch_rollover_size_in_mbs = 100
    batch_rollover_time_in_ms  = 60000
  }

  freeform_tags = {
    "Provisioner" = "Terraform"
  }

  depends_on = [
    oci_identity_policy.service_connector_policy,
    oci_logging_log.vcn_flow_log,
  ]
}

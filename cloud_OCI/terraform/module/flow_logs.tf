locals {
  compartment_id = var.compartment_id != "" ? var.compartment_id : var.tenancy_id
}

resource "oci_logging_log_group" "kentik_log_group" {
  compartment_id = local.compartment_id
  display_name   = "${var.log_prefix}-vcn-flow-logs"

  freeform_tags = {
    "Provisioner" = "Terraform"
  }
}

resource "oci_core_capture_filter" "kentik_capture_filter" {
  compartment_id = local.compartment_id
  display_name   = "${var.log_prefix}-capture-filter"
  filter_type    = "FLOWLOG"

  flow_log_capture_filter_rules {
    is_enabled    = true
    flow_log_type = "ALL"
    rule_action   = "INCLUDE"
    sampling_rate = var.flow_log_sampling_rate
  }

  freeform_tags = {
    "Provisioner" = "Terraform"
  }
}

resource "oci_logging_log" "vcn_flow_log" {
  count        = length(var.vcn_id_list)
  display_name = "${var.log_prefix}-vcn-flow-log-${count.index}"
  log_group_id = oci_logging_log_group.kentik_log_group.id
  log_type     = "SERVICE"

  configuration {
    source {
      category    = "all"
      resource    = var.vcn_id_list[count.index]
      service     = "flowlogs"
      source_type = "OCISERVICE"
    }
    compartment_id = local.compartment_id
  }

  freeform_tags = {
    "Provisioner" = "Terraform"
  }

  depends_on = [oci_core_capture_filter.kentik_capture_filter]
}

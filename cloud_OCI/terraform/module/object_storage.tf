data "oci_objectstorage_namespace" "ns" {
  compartment_id = local.compartment_id
}

resource "oci_objectstorage_bucket" "kentik_logs" {
  compartment_id = local.compartment_id
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "${var.bucket_name_prefix}-flow-logs-${terraform.workspace}"
  access_type    = "NoPublicAccess"

  freeform_tags = {
    "Provisioner" = "Terraform"
  }
}

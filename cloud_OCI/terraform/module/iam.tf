# IAM group and optional user for Kentik access.
# Groups and users must be created in the root tenancy compartment.
resource "oci_identity_group" "kentik_group" {
  compartment_id = var.tenancy_id
  name           = "${var.iam_prefix}-group"
  description    = "Group granting Kentik read access to OCI resources"
}

resource "oci_identity_user" "kentik_user" {
  count          = var.create_user ? 1 : 0
  compartment_id = var.tenancy_id
  name           = "${var.iam_prefix}-user"
  description    = "User for Kentik cloud integration"
  email          = var.kentik_user_email
}

resource "oci_identity_user_group_membership" "kentik_membership" {
  count    = var.create_user ? 1 : 0
  group_id = oci_identity_group.kentik_group.id
  user_id  = oci_identity_user.kentik_user[0].id
}

resource "oci_identity_api_key" "kentik_api_key" {
  count     = var.create_user && var.kentik_api_public_key != "" ? 1 : 0
  user_id   = oci_identity_user.kentik_user[0].id
  key_value = var.kentik_api_public_key
}

# Grants Kentik read access to networking, compute, and storage metadata.
resource "oci_identity_policy" "kentik_policy" {
  compartment_id = var.tenancy_id
  name           = "${var.iam_prefix}-policy"
  description    = "Policy granting Kentik read access to OCI resources for cloud export"
  statements = [
    "Allow group ${oci_identity_group.kentik_group.name} to INSPECT tenancies in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ instance-family in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ vcns in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ subnets in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ route-tables in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ security-lists in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ network-security-groups in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ cross-connects in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ ipsec-connections in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ virtual-circuits in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ local-peering-gateways in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ nat-gateways in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ internet-gateways in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ drgs in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ drg-attachments in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ cpes in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ buckets in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ objects in tenancy WHERE target.bucket.name='${oci_objectstorage_bucket.kentik_logs.name}'",
    "Allow group ${oci_identity_group.kentik_group.name} to INSPECT metrics in tenancy",
    "Allow group ${oci_identity_group.kentik_group.name} to READ metrics in tenancy",
  ]
}

# Allows the Service Connector to write log objects to the Kentik bucket.
# Must be created at the tenancy level to use the compartment id syntax.
resource "oci_identity_policy" "service_connector_policy" {
  compartment_id = var.tenancy_id
  name           = "${var.iam_prefix}-service-connector-policy"
  description    = "Policy allowing the Service Connector to write VCN flow logs to Object Storage"
  statements = [
    "Allow any-user to manage objects in compartment id ${local.compartment_id} where all {request.principal.type='serviceconnector', target.bucket.name='${oci_objectstorage_bucket.kentik_logs.name}', request.principal.compartment.id='${local.compartment_id}'}"
  ]
}

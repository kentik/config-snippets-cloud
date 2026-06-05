output "bucket_name" {
  description = "Name of the Object Storage bucket receiving flow logs"
  value       = oci_objectstorage_bucket.kentik_logs.name
}

output "bucket_namespace" {
  description = "Object Storage namespace for the bucket"
  value       = data.oci_objectstorage_namespace.ns.namespace
}

output "log_group_id" {
  description = "OCID of the Log Group created for VCN flow logs"
  value       = oci_logging_log_group.kentik_log_group.id
}

output "service_connector_id" {
  description = "OCID of the Service Connector routing flow logs to Object Storage"
  value       = oci_sch_service_connector.kentik_connector.id
}

output "kentik_group_id" {
  description = "OCID of the IAM group created for Kentik access"
  value       = oci_identity_group.kentik_group.id
}

output "kentik_user_id" {
  description = "OCID of the IAM user created for Kentik access (null if create_user is false)"
  value       = var.create_user ? oci_identity_user.kentik_user[0].id : null
}

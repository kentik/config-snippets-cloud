output "bucket_name" {
  description = "Name of the Object Storage bucket receiving flow logs"
  value       = module.kentik_oci_integration.bucket_name
}

output "bucket_namespace" {
  description = "Object Storage namespace"
  value       = module.kentik_oci_integration.bucket_namespace
}

output "log_group_id" {
  description = "OCID of the Log Group created for VCN flow logs"
  value       = module.kentik_oci_integration.log_group_id
}

output "service_connector_id" {
  description = "OCID of the Service Connector routing flow logs to Object Storage"
  value       = module.kentik_oci_integration.service_connector_id
}

output "kentik_user_id" {
  description = "OCID of the IAM user created for Kentik access"
  value       = module.kentik_oci_integration.kentik_user_id
}

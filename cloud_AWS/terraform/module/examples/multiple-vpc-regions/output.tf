output "kentik_iam_role_arn" {
  value = module.role_and_cloud_export.iam_role_arn
}

output "kentik_bucket_name" {
  value = module.kentik_aws_integration_vpc1.bucket_name_list
}

output "kentik_bucket_name_2" {
  value = module.kentik_aws_integration_vpc2.bucket_name_list
}
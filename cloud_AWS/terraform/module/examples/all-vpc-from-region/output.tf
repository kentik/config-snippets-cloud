output "kentik_iam_role_arn" {
  value = module.kentik_aws_integration.iam_role_arn
}

output "kentik_bucket_name" {
  value =  module.kentik_aws_integration.bucket_name_list
}

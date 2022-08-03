output "kentik_bucket_name" {
  value = module.s3_bucket_resources.bucket_name_list
}

output "kentik_bucket_arn_list" {
  value = module.s3_bucket_resources.bucket_arn_list
}
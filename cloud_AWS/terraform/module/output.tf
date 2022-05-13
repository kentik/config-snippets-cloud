output "iam_role_arn" {
  value = aws_iam_role.kentik_role.*.arn
}

output "bucket_name_list" {
  value = [
    for bucketobject in aws_s3_bucket.vpc_logs :
    (var.s3_flowlogs_path == "" ? bucketobject.bucket : "${bucketobject.bucket}/${var.s3_flowlogs_path}")
  ]
}

output "bucket_arn_list" {
  value = aws_s3_bucket.vpc_logs.*.arn
}

output "regions" {
  value = [var.region]
}

terraform {
  required_providers {
    kentik-cloudexport = {
      source = "kentik/kentik-cloudexport"
    }
  }
}

resource "kentik-cloudexport_item" "aws_export" {
  # Create when bucket_name_list or plan_id is set
  count = var.bucket_name_list != null ? length(var.bucket_name_list) : var.plan_id == "" ? 0 : 1

  name           = var.bucket_name_list != null ? "${var.name}-${terraform.workspace}${count.index}" : "${var.name}-${terraform.workspace}" # cloudexport name must be unique
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "aws"
  aws {
    bucket = var.bucket_name_list != null ? "${var.bucket_name_list[count.index]}/" : join(", ",[
      for bucketobject in aws_s3_bucket.vpc_logs :
      (var.s3_flowlogs_path == "" ? bucketobject.bucket : "${bucketobject.bucket}/${var.s3_flowlogs_path}")
    ])
    iam_role_arn      = var.create_role ? aws_iam_role.kentik_role[0].arn : ""
    region            = var.regions != null ? var.regions[count.index] : var.region
    delete_after_read = var.delete_after_read
    multiple_buckets  = var.multiple_buckets
  }
}
terraform {
  required_providers {
    kentik-cloudexport = {
      source = "kentik/kentik-cloudexport"
    }
  }
}

resource "kentik-cloudexport_item" "aws_export" {
  # Create when bucket_name_list or plan_id is set
  count = length(var.bucket_region_name) != 0 ? length(var.bucket_region_name) : var.plan_id == "" ? 0 : 1

  name           = length(var.bucket_region_name) != 0 ? "${var.name}-${terraform.workspace}-${count.index}" : "${var.name}-${terraform.workspace}" # cloudexport name must be unique
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "aws"
  aws {
    bucket = length(var.bucket_region_name) != 0 ? var.bucket_region_name[count.index][1]  : join(", ",[
      for bucketobject in aws_s3_bucket.vpc_logs :
      (var.s3_flowlogs_path == "" ? bucketobject.bucket : "${bucketobject.bucket}/${var.s3_flowlogs_path}")
    ])
    iam_role_arn      = var.create_role ? aws_iam_role.kentik_role[0].arn : ""
    region            = length(var.bucket_region_name) != 0 ? var.bucket_region_name[count.index][0] : var.region
    delete_after_read = var.delete_after_read
    multiple_buckets  = var.multiple_buckets
  }
}
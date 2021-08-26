terraform {
  required_providers {
    kentik-cloudexport = {
      source  = "kentik/kentik-cloudexport"
      version = ">= 0.2.0"
    }
  }
}

resource "kentik-cloudexport_item" "aws_export" {
  name           = var.name
  type           = "CLOUD_EXPORT_TYPE_KENTIK_MANAGED"
  enabled        = var.enabled
  description    = var.description
  plan_id        = var.plan_id
  cloud_provider = "aws"
  aws {
    bucket = join(", ", [
      for bucketobject in aws_s3_bucket.vpc_logs :
      (var.s3_flowlogs_path == "" ? bucketobject.bucket : "${bucketobject.bucket}/${var.s3_flowlogs_path}")
    ])
    iam_role_arn      = aws_iam_role.kentik_role.*.arn[0]
    region            = var.region
    delete_after_read = var.delete_after_read
    multiple_buckets  = var.multiple_buckets
  }
}